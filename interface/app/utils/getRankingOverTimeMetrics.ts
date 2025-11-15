export async function getRankingOverTimeMetrics(params: {
  brand: string;
  brand_report_id: string;
  start_date?: string | null;
  end_date?: string | null;
  model?: string;
}): Promise<any> {
  try {
    return await $fetch("/api/report/metrics/ranking-over-time", {
      method: "GET",
      params,
    });
  } catch (error) {
    console.error("Erreur Ranking Over Time:", error);
    return null;
  }
}
