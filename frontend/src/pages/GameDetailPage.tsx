import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { GameDetail, fetchGameDetail } from "../api/client";
import PriceChart from "../components/PriceChart";

function GameDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<GameDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      if (!id) return;
      setLoading(true);
      try {
        const res = await fetchGameDetail(id);
        setData(res);
      } catch (err) {
        console.error(err);
        setError("Failed to load game details.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  if (loading) return <div className="card">Loading...</div>;
  if (error) return <div className="card">{error}</div>;
  if (!data) return null;

  const { game, current_prices, history, metadata } = data;

  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
        {game.cover_image_url ? (
          <img
            src={game.cover_image_url}
            alt={game.title}
            style={{ width: 140, height: 140, objectFit: "cover", borderRadius: 12 }}
          />
        ) : (
          <div
            style={{
              width: 140,
              height: 140,
              borderRadius: 12,
              background: "rgba(255,255,255,0.08)"
            }}
          />
        )}
        <div>
          <h2 style={{ margin: 0 }}>{game.title}</h2>
          {metadata?.tags && (
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {metadata.tags.map((tag) => (
                <span key={tag} className="pill">
                  {tag}
                </span>
              ))}
            </div>
          )}
          {game.store_url && (
            <div style={{ marginTop: 8 }}>
              <a href={game.store_url} target="_blank" rel="noreferrer" className="pill">
                View on store
              </a>
            </div>
          )}
        </div>
      </div>

      {metadata?.description && <p className="muted">{metadata.description}</p>}

      <div>
        <h3 className="section-title">Current prices</h3>
        {current_prices.length === 0 ? (
          <div className="muted">No price data yet. Try refreshing from backend.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Store</th>
                <th>Price</th>
                <th>List</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {current_prices.map((p) => (
                <tr key={`${p.store_name}-${p.timestamp}`}>
                  <td>{p.store_name}</td>
                  <td>${p.price.toFixed(2)}</td>
                  <td>{p.list_price ? `$${p.list_price.toFixed(2)}` : "-"}</td>
                  <td>{new Date(p.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div>
        <h3 className="section-title">Price history</h3>
        <PriceChart data={history} />
      </div>

      <div style={{ textAlign: "right" }}>
        <Link to="/" className="pill">
          Back to watchlist
        </Link>
      </div>
    </div>
  );
}

export default GameDetailPage;
