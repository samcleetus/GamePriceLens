import { SearchResult } from "../api/client";

interface Props {
  result: SearchResult;
  onAdd: (apiGameId: string) => void;
  added?: boolean;
}

function GameCard({ result, onAdd, added }: Props) {
  return (
    <div className="card" style={{ display: "flex", gap: 12, alignItems: "center" }}>
      {result.thumb ? (
        <img
          src={result.thumb}
          alt={result.title}
          style={{ width: 72, height: 72, objectFit: "cover", borderRadius: 10 }}
        />
      ) : (
        <div
          style={{
            width: 72,
            height: 72,
            borderRadius: 10,
            background: "rgba(255,255,255,0.08)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#94a3b8",
            fontSize: 12
          }}
        >
          No art
        </div>
      )}
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700 }}>{result.title}</div>
        <div className="muted" style={{ fontSize: 13 }}>
          {result.cheapestPrice ? `Cheapest: $${result.cheapestPrice}` : "Price unknown"}
        </div>
      </div>
      <button className="button secondary" onClick={() => onAdd(result.api_game_id)} disabled={added}>
        {added ? "In watchlist" : "Add"}
      </button>
    </div>
  );
}

export default GameCard;
