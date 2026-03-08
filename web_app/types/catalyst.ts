// types/catalyst.ts
export type Catalyst = {
  catalyst_id: string;
  tic: string;
  date: string;
  catalyst_type: string;
  title: string;
  summary: string;
  state: string;
  sentiment: number;
  time_horizon: number;
  magnitude: number;
  impact_area: string;
  mention_count: number;
  chunk_ids: string[];
  source_types: string[];
  citations: string[];
  urls: string[];
  created_at: string;
  updated_at: string;
}

export enum CatalystSentiment {
  Bullish = 1,
  Neutral = 0,
  Bearish = -1,
}

export enum ImpactMagnitude {
  Major = 1,
  Moderate = 0,
  Minor = -1,
}

export enum TimeHorizon {
  ShortTerm = 1, // e.g., days to weeks
  MediumTerm = 2, // e.g., weeks to months
  LongTerm = 3, // e.g., months to years
}