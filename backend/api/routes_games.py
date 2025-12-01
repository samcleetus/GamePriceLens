from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..deps import get_db
from ..services import price_api, scraper

router = APIRouter()


@router.post("/games", response_model=schemas.GameRead)
def add_game(game_in: schemas.GameCreate, db: Session = Depends(get_db)) -> schemas.GameRead:
    existing = crud.get_game_by_api_id(db, game_in.api_game_id)
    if existing:
        return existing  # type: ignore

    try:
        details = price_api.get_game_details(game_in.api_game_id)
        title, thumb, snapshots = price_api.extract_snapshot_rows(details)
    except price_api.CheapSharkError as exc:
        raise HTTPException(status_code=503, detail=f"CheapShark unavailable: {exc}")

    steam_app_id = details.get("info", {}).get("steamAppID") if isinstance(details, dict) else None
    derived_store_url = f"https://store.steampowered.com/app/{steam_app_id}" if steam_app_id else None

    # use provided values if available, otherwise fallback to CheapShark data
    game_data = schemas.GameCreate(
        api_game_id=game_in.api_game_id,
        title=game_in.title or title,
        cover_image_url=game_in.cover_image_url or thumb,
        store_url=game_in.store_url or derived_store_url,
    )
    game = crud.create_game(db, game_data)

    if snapshots:
        crud.upsert_price_snapshots(db, game.id, snapshots)

    return game  # type: ignore


@router.get("/games", response_model=List[schemas.GameSummary])
def list_games(db: Session = Depends(get_db)) -> List[schemas.GameSummary]:
    games = crud.get_games_with_summary(db)
    return games


@router.get("/games/{game_id}", response_model=schemas.GameDetailResponse)
def game_detail(game_id: int, db: Session = Depends(get_db)) -> schemas.GameDetailResponse:
    game = crud.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    current_prices = crud.get_latest_prices_by_store(db, game_id)
    history = crud.get_price_history(db, game_id)
    metadata = crud.get_metadata(db, game_id)

    return schemas.GameDetailResponse(
        game=schemas.GameRead.from_orm(game),
        current_prices=[schemas.PriceSnapshotRead.from_orm(p) for p in current_prices],
        history=history,
        metadata=metadata,
    )


@router.post("/games/{game_id}/refresh_metadata", response_model=schemas.GameMetadataRead)
def refresh_metadata(game_id: int, db: Session = Depends(get_db)) -> schemas.GameMetadataRead:
    game = crud.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if not game.store_url:
        raise HTTPException(status_code=400, detail="Game has no store_url to scrape")
    try:
        scraper.update_game_metadata(db, game)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    metadata = crud.get_metadata(db, game_id)
    if metadata is None:
        raise HTTPException(status_code=500, detail="Failed to store metadata")
    return metadata
