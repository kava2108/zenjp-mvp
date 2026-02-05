export interface ScoreDetail {
  per: number | null;
  per_score: number | null;
  pbr: number | null;
  pbr_score: number | null;
  dividend_yield: number | null;
  dividend_score: number | null;
  revenue_growth_rate: number | null;
  rsi: number | null;
  rsi_score: number | null;
  volume_change_rate: number | null;
  volume_change_score: number | null;
  volume_score?: number | null;
}

export interface MarketComparison {
  total_diff: number;
  value_diff: number;
  growth_diff: number;
  momentum_diff: number;
}

export interface ScoreData {
  stock_code: string;
  stock_name: string;
  total_score: number;
  rank: string;
  value_score: number;
  growth_score: number;
  momentum_score: number;
  score_date: string;
  details: ScoreDetail;
  market_comparison: MarketComparison;
  updated_at: string;
}

export interface Stock {
  code: string;
  name: string;
}

export const STOCKS: Stock[] = [
  { code: '7203', name: 'トヨタ自動車' },
  { code: '6758', name: 'ソニーグループ' },
  { code: '9984', name: 'ソフトバンクグループ' }
];
