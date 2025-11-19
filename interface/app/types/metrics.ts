export type MetricKey = 'mentions' | 'shareOfVoice' | 'coverage' | 'position' | 'ranking';

export interface MetricConfig {
  key: MetricKey;
  title: string;
  icon: string;
  endpoint: string;
  fullWidth?: boolean;
}

export interface RankingEntry {
  rank?: number;
  brand_name?: string;
  mention_count?: number;
}
