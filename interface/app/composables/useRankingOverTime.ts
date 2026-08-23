import { getRankingOverTimeMetrics } from "~/utils/getRankingOverTimeMetrics";
import type {
  AreaCategories,
  ChartRow,
  RankingOverTimeResponse,
} from "../types/ranking";

const colorPalette = [
  "#2563eb",
  "#dc2626",
  "#f97316",
  "#16a34a",
  "#9333ea",
  "#0ea5e9",
  "#facc15",
  "#14b8a6",
];

export function useRankingOverTime() {
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Data / categories for ranks and mentions
  const rankData = ref<ChartRow[]>([]);
  const rankCategories = ref<AreaCategories>({});
  const mentionData = ref<ChartRow[]>([]);
  const mentionCategories = ref<AreaCategories>({});

  //format date to ISO (yyyy-mm-dd) or null if invalid
  const isoDateForPoint = (value?: string) => {
    if (!value) return null;
    const d = new Date(value);
    if (isNaN(d.getTime())) return null;
    return d.toISOString().slice(0, 10);
  };

  // Build series data structure from ranking entries
  const buildSeries = (
    ranking: any[] = [],
    valueKey: "rank" | "mention_count",
  ) => {
    const brandOrder: string[] = [];
    const rows = new Map<string, ChartRow>();

    for (const entry of ranking || []) {
      const rawName = (entry.brand_name?.trim() as string) || "Unknown";
      const brandKey = rawName.toLowerCase().replace(/[^a-z0-9]+/gi, "_");
      if (!brandOrder.includes(brandKey)) brandOrder.push(brandKey);

      for (const point of entry.points || []) {
        const isoDate = isoDateForPoint(point.date);
        if (isoDate === null) continue;

        if (!rows.has(isoDate)) rows.set(isoDate, { date: isoDate });
        const row = rows.get(isoDate)!;
        const baseValue =
          valueKey === "rank" ? point.rank : point.mention_count;
        if (typeof baseValue === "number") row[brandKey] = baseValue;
      }
    }

    // Build categories with colors
    const categories = brandOrder.reduce<AreaCategories>(
      (acc, brand, index) => {
        const paletteColor =
          colorPalette[index % colorPalette.length] ?? "#64748b";
        const rawBrandName =
          ranking
            .find(
              (r) =>
                (r.brand_name
                  ?.trim()
                  .toLowerCase()
                  .replace(/[^a-z0-9]+/gi, "_") ?? "") === brand,
            )
            ?.brand_name?.trim() || brand;
        acc[brand] = { name: rawBrandName, color: paletteColor };
        return acc;
      },
      {},
    );

    // Build series array sorted by date
    const series = [...rows.entries()]
      .sort(
        (a, b) =>
          new Date(String(a[0])).getTime() - new Date(String(b[0])).getTime(),
      )
      .map(([, payload]) => payload);
    const hasValues = series.some((r) =>
      Object.keys(r).some((k) => k !== "date" && typeof r[k] === "number"),
    );
    return { categories, series, hasValues };
  };

  // Process response and set data or categories
  const setRankingFromResponse = async (
    response: RankingOverTimeResponse | any,
  ) => {
    loading.value = true;
    error.value = null;
    const ranking = (response?.data?.ranking as any[]) || [];

    // Create two series: ranks and mentions
    const rankSeries = buildSeries(ranking, "rank");
    const mentionSeries = buildSeries(ranking, "mention_count");

    if (rankSeries.hasValues) {
      rankCategories.value = rankSeries.categories;
      rankData.value = rankSeries.series;
    } else {
      rankCategories.value = {};
      rankData.value = [];
    }

    if (mentionSeries.hasValues) {
      mentionCategories.value = mentionSeries.categories;
      mentionData.value = mentionSeries.series;
    } else {
      mentionCategories.value = {};
      mentionData.value = [];
    }

    loading.value = false;
  };

  // Fetch data from the server and delegate to setRankingFromResponse
  const fetchRankingOverTime = async (params: {
    brand: string;
    brand_report_id: string;
    model?: string;
    start_date?: string | null;
    end_date?: string | null;
  }) => {
    if (!params.brand || !params.brand_report_id) {
      rankData.value = [];
      mentionData.value = [];
      rankCategories.value = {};
      mentionCategories.value = {};
      return;
    }
    loading.value = true;
    error.value = null;
    try {
      const response = await getRankingOverTimeMetrics(params);
      await setRankingFromResponse(response);
    } catch (err) {
      console.error("fetchRankingOverTime error", err);
      error.value = "Unable to load ranking over time";
    } finally {
      loading.value = false;
    }
  };

  // Format X-axis labels for ranks and mentions
  const formatXLabel = (tick: any, i?: number, data?: ChartRow[]) => {
    if (typeof tick === "number" && typeof data?.[tick]?.date === "string") {
      const d = new Date(data[tick].date);
      return isNaN(d.getTime())
        ? String(data[tick].date)
        : new Intl.DateTimeFormat("en-US", { dateStyle: "medium" }).format(d);
    }
    if (typeof tick === "string" || tick instanceof Date) {
      const d = new Date(tick);
      return isNaN(d.getTime())
        ? String(tick)
        : new Intl.DateTimeFormat("en-US", { dateStyle: "medium" }).format(d);
    }
    if (typeof i === "number" && data?.[i]?.date) {
      const d = new Date(data[i].date);
      return isNaN(d.getTime())
        ? String(data[i].date)
        : new Intl.DateTimeFormat("en-US", { dateStyle: "medium" }).format(d);
    }
    return "";
  };

  // formatters for rank and mention data
  const formatRankXLabel = (tick: any, i?: number) =>
    formatXLabel(tick, i, rankData.value);
  const formatMentionXLabel = (tick: any, i?: number) =>
    formatXLabel(tick, i, mentionData.value);

  return {
    loading,
    error,
    rankCategories,
    mentionCategories,
    rankData,
    mentionData,
    fetchRankingOverTime,
    setRankingFromResponse,
    formatRankXLabel,
    formatMentionXLabel,
  };
}
