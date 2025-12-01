import { FormEvent, useState } from "react";

interface Props {
  onSearch: (query: string) => void;
  loading?: boolean;
}

function SearchBar({ onSearch, loading }: Props) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim().length === 0) return;
    onSearch(query.trim());
  };

  return (
    <form className="card" onSubmit={handleSubmit} style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
        <input
          type="text"
          placeholder="Search for a game..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            flex: 1,
            padding: "12px 14px",
            borderRadius: 10,
            border: "1px solid rgba(255,255,255,0.08)",
            background: "rgba(255,255,255,0.05)",
            color: "#e2e8f0"
          }}
        />
        <button className="button" type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </div>
    </form>
  );
}

export default SearchBar;
