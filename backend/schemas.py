from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class GameBase(BaseModel):
    title: Optional[str] = None
    api_game_id: str
    store_url: Optional[str] = None
    cover_image_url: Optional[str] = None


class GameCreate(GameBase):
    api_game_id: str


class GameRead(GameBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GameSummary(GameRead):
    best_price: Optional[float] = None
    best_store: Optional[str] = None
    last_updated: Optional[datetime] = None


class PriceSnapshotRead(BaseModel):
    store_name: str
    price: float
    list_price: Optional[float] = None
    currency: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class PriceHistoryPoint(BaseModel):
    date: date
    min_price: float


class GameMetadataRead(BaseModel):
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    last_scraped_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GameDetailResponse(BaseModel):
    game: GameRead
    current_prices: List[PriceSnapshotRead]
    history: List[PriceHistoryPoint]
    metadata: Optional[GameMetadataRead] = None


class SearchResult(BaseModel):
    api_game_id: str
    title: str
    thumb: Optional[str] = None
    cheapestPrice: Optional[float] = None


class RefreshSummary(BaseModel):
    games_processed: int
    snapshots_inserted: int
