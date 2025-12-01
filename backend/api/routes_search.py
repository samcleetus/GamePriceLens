from typing import List

from fastapi import APIRouter, HTTPException, Query

from .. import schemas
from ..services import price_api

router = APIRouter()


@router.get("/search", response_model=List[schemas.SearchResult])
def search_games(q: str = Query(..., description="Search query")) -> List[schemas.SearchResult]:
    try:
        results = price_api.search_games(q)
    except price_api.CheapSharkError as exc:
        raise HTTPException(status_code=503, detail=f"CheapShark unavailable: {exc}")
    return [schemas.SearchResult(**item) for item in results]
