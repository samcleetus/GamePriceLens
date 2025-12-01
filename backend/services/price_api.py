from typing import Dict, List, Optional, Tuple

import requests


CHEAPSHARK_BASE = "https://www.cheapshark.com/api/1.0"


class CheapSharkError(Exception):
    pass


def _get(url: str, params: Optional[dict] = None) -> dict | List[dict]:
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:  # pragma: no cover - network failures not under test
        raise CheapSharkError(str(exc)) from exc


def search_games(query: str) -> List[Dict[str, Optional[str]]]:
    data = _get(f"{CHEAPSHARK_BASE}/games", params={"title": query})
    results: List[Dict[str, Optional[str]]] = []
    for item in data:
        results.append(
            {
                "api_game_id": item.get("gameID"),
                "title": item.get("external"),
                "thumb": item.get("thumb"),
                "cheapestPrice": float(item["cheapest"]) if item.get("cheapest") else None,
            }
        )
    return results


def get_game_details(api_game_id: str) -> Dict:
    data = _get(f"{CHEAPSHARK_BASE}/games", params={"id": api_game_id})
    return data


def extract_snapshot_rows(game_details: Dict) -> Tuple[str, Optional[str], List[Tuple[str, float, Optional[float], str]]]:
    """
    Returns tuple of (title, cover_image_url, snapshots)
    snapshots is list of (store_name, price, list_price, currency)
    """
    info = game_details.get("info", {})
    title = info.get("title") or ""
    thumb = info.get("thumb")
    deals = game_details.get("deals", [])
    snapshots: List[Tuple[str, float, Optional[float], str]] = []
    for deal in deals:
        store_name = deal.get("storeName") or f"Store {deal.get('storeID', '')}"
        price = float(deal.get("price", 0))
        list_price = float(deal["retailPrice"]) if deal.get("retailPrice") else None
        snapshots.append((store_name, price, list_price, "USD"))
    return title, thumb, snapshots
