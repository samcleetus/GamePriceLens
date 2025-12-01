import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api"
});

export interface SearchResult {
  api_game_id: string;
  title: string;
  thumb?: string;
  cheapestPrice?: number;
}

export interface GameSummary {
  id: number;
  title: string;
  api_game_id: string;
  cover_image_url?: string;
  store_url?: string;
  best_price?: number;
  best_store?: string;
  last_updated?: string;
  created_at?: string;
  updated_at?: string;
}

export interface PriceSnapshot {
  store_name: string;
  price: number;
  list_price?: number;
  currency: string;
  timestamp: string;
}

export interface PriceHistoryPoint {
  date: string;
  min_price: number;
}

export interface GameMetadata {
  description?: string | null;
  tags?: string[] | null;
  last_scraped_at?: string | null;
}

export interface GameDetail {
  game: GameSummary & { api_game_id: string; store_url?: string };
  current_prices: PriceSnapshot[];
  history: PriceHistoryPoint[];
  metadata?: GameMetadata | null;
}

export const fetchSearchResults = async (query: string) => {
  const res = await api.get<SearchResult[]>("/search", { params: { q: query } });
  return res.data;
};

export const addGameToWatchlist = async (api_game_id: string) => {
  const res = await api.post("/games", { api_game_id });
  return res.data;
};

export const fetchWatchlist = async () => {
  const res = await api.get<GameSummary[]>("/games");
  return res.data;
};

export const fetchGameDetail = async (id: string) => {
  const res = await api.get<GameDetail>(`/games/${id}`);
  return res.data;
};
