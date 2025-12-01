import { useEffect, useState } from "react";
import {
  SearchResult,
  GameSummary,
  fetchSearchResults,
  addGameToWatchlist,
  fetchWatchlist
} from "../api/client";
import SearchBar from "../components/SearchBar";
import GameCard from "../components/GameCard";
import GamesTable from "../components/GamesTable";

function HomePage() {
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [watchlist, setWatchlist] = useState<GameSummary[]>([]);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [loadingWatchlist, setLoadingWatchlist] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadWatchlist = async () => {
    setLoadingWatchlist(true);
    try {
      const data = await fetchWatchlist();
      setWatchlist(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load watchlist");
    } finally {
      setLoadingWatchlist(false);
    }
  };

  useEffect(() => {
    loadWatchlist();
  }, []);

  const handleSearch = async (query: string) => {
    setError(null);
    setLoadingSearch(true);
    try {
      const results = await fetchSearchResults(query);
      setSearchResults(results);
    } catch (err) {
      console.error(err);
      setError("Search failed. Please try again.");
    } finally {
      setLoadingSearch(false);
    }
  };

  const handleAdd = async (apiGameId: string) => {
    setError(null);
    try {
      await addGameToWatchlist(apiGameId);
      await loadWatchlist();
    } catch (err) {
      console.error(err);
      setError("Failed to add game to watchlist.");
    }
  };

  const isInWatchlist = (apiGameId: string) => watchlist.some((g) => g.api_game_id === apiGameId);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <SearchBar onSearch={handleSearch} loading={loadingSearch} />
      {error && <div className="card" style={{ borderColor: "#ef4444", color: "#fecdd3" }}>{error}</div>}

      {loadingSearch ? (
        <div className="card">Searching...</div>
      ) : searchResults.length > 0 ? (
        <div className="grid">
          {searchResults.map((result) => (
            <GameCard
              key={result.api_game_id}
              result={result}
              onAdd={handleAdd}
              added={isInWatchlist(result.api_game_id)}
            />
          ))}
        </div>
      ) : (
        <div className="card muted">Find a game to start tracking prices.</div>
      )}

      <div className="card" style={{ border: "none", background: "transparent", boxShadow: "none" }}>
        <h3 className="section-title">Watchlist</h3>
        {loadingWatchlist ? <div>Loading watchlist...</div> : <GamesTable games={watchlist} />}
      </div>
    </div>
  );
}

export default HomePage;
