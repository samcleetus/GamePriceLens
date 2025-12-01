import logging
import time
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from .. import crud, models

logger = logging.getLogger(__name__)


def fetch_steam_metadata(url: str) -> Dict[str, Optional[List[str] | str]]:
    try:
        time.sleep(0.5)  # be gentle to Steam
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network failures not under test
        logger.warning("Failed to fetch Steam page %s: %s", url, exc)
        return {"description": None, "tags": None}

    soup = BeautifulSoup(resp.text, "html.parser")
    description = None
    tags: Optional[List[str]] = None

    try:
        desc_node = soup.select_one("#game_area_description, .game_description_snippet")
        if desc_node:
            description = desc_node.get_text(strip=True)
    except Exception as exc:  # pragma: no cover - parsing errors are non-critical
        logger.warning("Failed to parse description: %s", exc)

    try:
        tag_nodes = soup.select(".glance_tags.popular_tags a.app_tag")
        if tag_nodes:
            tags = [tag.get_text(strip=True) for tag in tag_nodes if tag.get_text(strip=True)]
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to parse tags: %s", exc)

    return {"description": description, "tags": tags}


def update_game_metadata(db: Session, game: models.Game) -> models.GameMetadata:
    if not game.store_url:
        raise ValueError("Game has no store_url for scraping")
    metadata = fetch_steam_metadata(game.store_url)
    return crud.upsert_metadata(db, game.id, metadata)
