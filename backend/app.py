from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .api import routes_games, routes_refresh, routes_search

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GamePriceLens")

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_search.router, prefix="/api", tags=["search"])
app.include_router(routes_games.router, prefix="/api", tags=["games"])
app.include_router(routes_refresh.router, prefix="/api", tags=["refresh"])


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
