import logging
import threading
import time

from . import crud
from .database import SessionLocal
from .services import price_api

logger = logging.getLogger(__name__)

# Configuration: refresh interval in seconds (default: 1 hour)
REFRESH_INTERVAL = 3600


def refresh_prices_job():
    """Background job to refresh prices periodically"""
    while True:
        time.sleep(REFRESH_INTERVAL)
        logger.info("Starting scheduled price refresh...")
        db = SessionLocal()
        try:
            games = crud.list_games(db)
            games_processed = 0
            snapshots_inserted = 0

            for game in games:
                games_processed += 1
                try:
                    details = price_api.get_game_details(game.api_game_id)
                    _, _, snapshots = price_api.extract_snapshot_rows(details)
                    if snapshots:
                        count = crud.upsert_price_snapshots(db, game.id, snapshots)
                        snapshots_inserted += count
                except price_api.CheapSharkError as exc:
                    logger.error(f"Failed to refresh game {game.id} ({game.title}): {exc}")
                except Exception as exc:
                    logger.exception(f"Unexpected error refreshing game {game.id}: {exc}")

            logger.info(
                f"Price refresh complete. Processed {games_processed} games, "
                f"inserted {snapshots_inserted} snapshots."
            )
        except Exception as exc:
            logger.exception(f"Price refresh job failed: {exc}")
        finally:
            db.close()


def start_scheduler():
    """Start the background price refresh scheduler"""
    logger.info(f"Starting price refresh scheduler (interval: {REFRESH_INTERVAL}s)")
    thread = threading.Thread(target=refresh_prices_job, daemon=True)
    thread.start()
