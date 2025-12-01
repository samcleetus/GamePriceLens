from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..deps import get_db
from ..services import price_api

router = APIRouter()


@router.post("/refresh", response_model=schemas.RefreshSummary)
def refresh_prices(db: Session = Depends(get_db)) -> schemas.RefreshSummary:
    games = crud.list_games(db)
    games_processed = 0
    snapshots_inserted = 0

    for game in games:
        games_processed += 1
        try:
            details = price_api.get_game_details(game.api_game_id)
            _, _, snapshots = price_api.extract_snapshot_rows(details)
        except price_api.CheapSharkError as exc:
            raise HTTPException(status_code=503, detail=f"CheapShark unavailable: {exc}")

        if snapshots:
            snapshots_inserted += crud.upsert_price_snapshots(db, game.id, snapshots)

    return schemas.RefreshSummary(games_processed=games_processed, snapshots_inserted=snapshots_inserted)
