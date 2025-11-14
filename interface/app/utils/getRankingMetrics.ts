export async function getRankingMetrics(params: {
  brand: string;
  brand_report_id: string;
  start_date?: string | null;
  end_date?: string | null;
  model?: string;
}): Promise<any> {
  try {
    return await $fetch("/api/report/metrics/ranking", {
      method: "GET",
      params,
    });
  } catch (error) {
    console.error("Erreur Ranking:", error);
    return null;
  }
}
