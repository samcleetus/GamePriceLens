# GamePriceLens

GamePriceLens is a small FastAPI + React app that tracks PC game prices from CheapShark, lets you build a watchlist, and shows a simple price history.

## Backend (FastAPI)

- Install deps: `pip install -r backend/requirements.txt`
- Run dev server: `uvicorn backend.app:app --reload`
- Default DB: SQLite at `./gamepricelens.db` (override with `DATABASE_URL`)
- Useful endpoints:
  - `GET /api/search?q=...` – search CheapShark
  - `POST /api/games` – add a game by `api_game_id`
  - `POST /api/refresh` – fetch latest prices for all games
  - `POST /api/games/{id}/refresh_metadata` – scrape Steam page if `store_url` is set

## Frontend (Vite + React + TS)

- From `frontend/`: `npm install`
- Start dev server: `npm run dev` (defaults to http://localhost:5173)
- API base URL can be overridden with `VITE_API_BASE_URL` (defaults to `http://localhost:8000/api`)

## Project Structure

- `backend/` – FastAPI app (`app.py`), models, CRUD helpers, CheapShark client, and Steam scraper.
- `frontend/` – Vite React app with simple pages for watchlist and game detail.

## Notes

- Light Steam scraping uses `requests` + `BeautifulSoup`; failures are logged and ignored.
- CORS is enabled for `http://localhost:5173`.
- Price history aggregates minimum price per day from stored snapshots.
