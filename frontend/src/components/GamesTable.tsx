import { Link } from "react-router-dom";
import { GameSummary } from "../api/client";

interface Props {
  games: GameSummary[];
}

function GamesTable({ games }: Props) {
  if (games.length === 0) {
    return <div className="card muted">No games in your watchlist yet.</div>;
  }

  return (
    <div className="card" style={{ overflowX: "auto" }}>
      <table className="table">
        <thead>
          <tr>
            <th></th>
            <th>Game</th>
            <th>Best price</th>
            <th>Store</th>
            <th>Last updated</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {games.map((game) => (
            <tr key={game.id}>
              <td>
                {game.cover_image_url ? (
                  <img
                    src={game.cover_image_url}
                    alt={game.title}
                    style={{ width: 48, height: 48, borderRadius: 8, objectFit: "cover" }}
                  />
                ) : (
                  <div
                    style={{
                      width: 48,
                      height: 48,
                      borderRadius: 8,
                      background: "rgba(255,255,255,0.08)"
                    }}
                  />
                )}
              </td>
              <td>{game.title}</td>
              <td>{game.best_price ? `$${game.best_price}` : "-"}</td>
              <td>{game.best_store || "-"}</td>
              <td>{game.last_updated ? new Date(game.last_updated).toLocaleString() : "-"}</td>
              <td>
                <Link className="pill" to={`/game/${game.id}`}>
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default GamesTable;
