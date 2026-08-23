export type MetricKey =
  | "mentions"
  | "shareOfVoice"
  | "coverage"
  | "position"
  | "ranking";

export interface MetricConfig {
  key: MetricKey;
  title: string;
  icon: string;
}

export interface RankingEntry {
  rank?: number;
  brand_name?: string;
  mention_count?: number;
}

export interface MetricRequestParams {
  brand: string;
  brand_report_id: string;
  model?: string;
  start_date?: string | undefined;
  end_date?: string | undefined;
}
