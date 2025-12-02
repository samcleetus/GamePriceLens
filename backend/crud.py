from datetime import datetime
import json
import re
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas


def get_game_by_api_id(db: Session, api_game_id: str) -> Optional[models.Game]:
    return db.query(models.Game).filter(models.Game.api_game_id == api_game_id).first()


def get_game(db: Session, game_id: int) -> Optional[models.Game]:
    return db.query(models.Game).filter(models.Game.id == game_id).first()


def create_game(db: Session, game_data: schemas.GameCreate) -> models.Game:
    game = models.Game(
        title=game_data.title or "Unknown Game",
        api_game_id=game_data.api_game_id,
        store_url=game_data.store_url,
        cover_image_url=game_data.cover_image_url,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def list_games(db: Session) -> List[models.Game]:
    return db.query(models.Game).order_by(models.Game.created_at.desc()).all()


def compute_game_summary(
    game: models.Game, latest_prices: Optional[List[models.PriceSnapshot]] = None
) -> schemas.GameSummary:
    best_price = None
    best_store = None
    last_updated = None
    prices = latest_prices if latest_prices is not None else list(game.price_snapshots)
    if prices:
        last_updated = max(prices, key=lambda snap: snap.timestamp).timestamp
        best_snapshot = min(prices, key=lambda snap: snap.price)
        best_price = best_snapshot.price
        best_store = best_snapshot.store_name
    return schemas.GameSummary(
        id=game.id,
        title=game.title,
        api_game_id=game.api_game_id,
        store_url=game.store_url,
        cover_image_url=game.cover_image_url,
        created_at=game.created_at,
        updated_at=game.updated_at,
        best_price=best_price,
        best_store=best_store,
        last_updated=last_updated,
    )


def get_games_with_summary(db: Session) -> List[schemas.GameSummary]:
    games = list_games(db)
    summaries: List[schemas.GameSummary] = []
    for game in games:
        latest_prices = get_latest_prices_by_store(db, game.id)
        summaries.append(compute_game_summary(game, latest_prices))
    return summaries


def get_latest_prices_by_store(db: Session, game_id: int) -> List[models.PriceSnapshot]:
    subq = (
        db.query(
            models.PriceSnapshot.store_name,
            func.max(models.PriceSnapshot.timestamp).label("max_ts"),
        )
        .filter(models.PriceSnapshot.game_id == game_id)
        .group_by(models.PriceSnapshot.store_name)
        .subquery()
    )
    snapshots = (
        db.query(models.PriceSnapshot)
        .join(
            subq,
            (models.PriceSnapshot.store_name == subq.c.store_name)
            & (models.PriceSnapshot.timestamp == subq.c.max_ts),
        )
        .filter(models.PriceSnapshot.game_id == game_id)
        .all()
    )
    return snapshots


def get_price_history(db: Session, game_id: int) -> List[schemas.PriceHistoryPoint]:
    rows = (
        db.query(
            func.date(models.PriceSnapshot.timestamp).label("date"),
            func.min(models.PriceSnapshot.price).label("min_price"),
        )
        .filter(models.PriceSnapshot.game_id == game_id)
        .group_by(func.date(models.PriceSnapshot.timestamp))
        .order_by(func.date(models.PriceSnapshot.timestamp))
        .all()
    )
    return [
        schemas.PriceHistoryPoint(date=row.date, min_price=row.min_price)  # type: ignore
        for row in rows
    ]


def upsert_price_snapshots(
    db: Session, game_id: int, snapshots: Iterable[Tuple[str, float, Optional[float], str]]
) -> int:
    """
    Inserts new price snapshots.
    snapshots: iterable of (store_name, price, list_price, currency)
    """
    count = 0
    timestamp = datetime.utcnow()
    for store_name, price, list_price, currency in snapshots:
        snap = models.PriceSnapshot(
            game_id=game_id,
            source="cheapshark",
            store_name=store_name,
            price=price,
            list_price=list_price,
            currency=currency,
            timestamp=timestamp,
        )
        db.add(snap)
        count += 1
    db.commit()
    return count


def normalize_store_names(db: Session, store_map: Dict[str, str]) -> int:
    """Replace placeholder store names like 'Store 3' with real names when available."""
    pattern = re.compile(r"Store\s+(\d+)$", re.IGNORECASE)
    snapshots = db.query(models.PriceSnapshot).filter(models.PriceSnapshot.store_name.ilike("Store %")).all()
    updated = 0
    for snap in snapshots:
        match = pattern.match(snap.store_name.strip())
        if not match:
            continue
        store_id = match.group(1)
        real_name = store_map.get(store_id)
        if real_name and snap.store_name != real_name:
            snap.store_name = real_name
            updated += 1
    if updated:
        db.commit()
    return updated


def upsert_metadata(db: Session, game_id: int, metadata: Dict[str, Optional[object]]) -> models.GameMetadata:
    existing = db.query(models.GameMetadata).filter(models.GameMetadata.game_id == game_id).first()
    tags = metadata.get("tags")
    tags_str = json.dumps(tags) if tags is not None else None
    if existing:
        existing.description = metadata.get("description")  # type: ignore
        existing.tags = tags_str
        existing.last_scraped_at = datetime.utcnow()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    meta = models.GameMetadata(
        game_id=game_id,
        description=metadata.get("description"),  # type: ignore
        tags=tags_str,
        last_scraped_at=datetime.utcnow(),
    )
    db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta


def get_metadata(db: Session, game_id: int) -> Optional[schemas.GameMetadataRead]:
    meta = db.query(models.GameMetadata).filter(models.GameMetadata.game_id == game_id).first()
    if not meta:
        return None
    tags = json.loads(meta.tags) if meta.tags else None
    return schemas.GameMetadataRead(
        description=meta.description,
        tags=tags,
        last_scraped_at=meta.last_scraped_at,
    )
