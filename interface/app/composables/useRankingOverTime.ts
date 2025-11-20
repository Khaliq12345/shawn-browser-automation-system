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

  const rankCategories = ref<AreaCategories>({});
  const positionCategories = ref<AreaCategories>({});
  const rankData = ref<ChartRow[]>([]);
  const positionData = ref<ChartRow[]>([]);

  const isoDateForPoint = (value?: string) => {
    if (!value) return null;
    const d = new Date(value);
    if (isNaN(d.getTime())) return null;
    return d.toISOString().slice(0, 10);
  };

  const buildSeries = (ranking: any[] = [], valueKey: "rank" | "position") => {
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
        const baseValue = valueKey === "rank" ? point.rank : point.position;
        if (typeof baseValue === "number") row[brandKey] = baseValue;
      }
    }

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

  const setRankingFromResponse = async (
    response: RankingOverTimeResponse | any,
  ) => {
    loading.value = true;
    error.value = null;
    let ranking: any[] = [];
    if (Array.isArray(response?.data?.ranking)) ranking = response.data.ranking;
    else if (Array.isArray(response?.ranking)) ranking = response.ranking;
    else if (Array.isArray(response)) ranking = response;
    else if (Array.isArray(response?.data)) ranking = response.data;

    const rankSeries = buildSeries(ranking, "rank");
    const positionSeries = buildSeries(ranking, "position");

    if (rankSeries.hasValues) {
      rankCategories.value = rankSeries.categories;
      rankData.value = rankSeries.series;
    } else {
      rankCategories.value = {};
      rankData.value = [];
    }

    if (positionSeries.hasValues) {
      positionCategories.value = positionSeries.categories;
      positionData.value = positionSeries.series;
    } else {
      positionCategories.value = {};
      positionData.value = [];
    }

    loading.value = false;
  };

  const fetchRankingOverTime = async (params: {
    brand: string;
    brand_report_id: string;
    model?: string;
    start_date?: string | null;
    end_date?: string | null;
  }) => {
    if (!params.brand || !params.brand_report_id) {
      rankData.value = [];
      positionData.value = [];
      rankCategories.value = {};
      positionCategories.value = {};
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

  const formatRankXLabel = (tick: any, i?: number) =>
    formatXLabel(tick, i, rankData.value);
  const formatPositionXLabel = (tick: any, i?: number) =>
    formatXLabel(tick, i, positionData.value);

  return {
    loading,
    error,
    rankCategories,
    positionCategories,
    rankData,
    positionData,
    fetchRankingOverTime,
    setRankingFromResponse,
    formatRankXLabel,
    formatPositionXLabel,
  };
}
