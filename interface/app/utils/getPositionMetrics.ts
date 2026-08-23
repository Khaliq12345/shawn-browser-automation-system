export async function getPositionMetrics(params: {
  brand: string;
  brand_report_id: string;
  start_date?: string | null;
  end_date?: string | null;
  model?: string;
}): Promise<any> {
  try {
    return await $fetch("/api/report/metrics/position", {
      method: "GET",
      params,
    });
  } catch (error) {
    console.error("Erreur Position:", error);
    return null;
  }
}
