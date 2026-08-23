export async function getCoverageMetrics(params: {
  brand: string;
  brand_report_id: string;
  start_date?: string | null;
  end_date?: string | null;
  model?: string;
}): Promise<any> {
  try {
    return await $fetch("/api/report/metrics/coverage", {
      method: "GET",
      params,
    });
  } catch (error) {
    console.error("Erreur Coverage:", error);
    return null;
  }
}
