from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    api_game_id = Column(String, unique=True, nullable=False, index=True)
    store_url = Column(String, nullable=True)
    cover_image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    price_snapshots = relationship("PriceSnapshot", back_populates="game", cascade="all, delete-orphan")
    metadata_entry = relationship("GameMetadata", back_populates="game", uselist=False, cascade="all, delete-orphan")


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    source = Column(String, nullable=False)
    store_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    list_price = Column(Float, nullable=True)
    currency = Column(String, nullable=False, default="USD")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    game = relationship("Game", back_populates="price_snapshots")


class GameMetadata(Base):
    __tablename__ = "game_metadata"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    last_scraped_at = Column(DateTime, nullable=True)

    game = relationship("Game", back_populates="metadata_entry")
