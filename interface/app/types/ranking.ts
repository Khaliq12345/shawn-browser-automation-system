export type AxisFormatter = (
  tick: number | string | Date,
  index?: number,
  ticks?: number[],
) => string;

export interface RankingPoint {
  date?: string;
  rank?: number;
  mention_count?: number;
}

export interface RankingEntryResponse {
  brand_name?: string;
  points?: RankingPoint[];
}

export interface RankingOverTimeResponse {
  data?: {
    ranking?: RankingEntryResponse[];
  };
}

export type AreaCategories = Record<string, { name: string; color: string }>;
export type ChartRow = Record<string, string | number> & { date: string };
