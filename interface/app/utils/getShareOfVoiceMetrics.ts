export async function getShareOfVoiceMetrics(params: {
  brand: string;
  brand_report_id: string;
  start_date?: string | null;
  end_date?: string | null;
  model?: string;
}): Promise<any> {
  try {
    return await $fetch("/api/report/metrics/share-of-voice", {
      method: "GET",
      params,
    });
  } catch (error) {
    console.error("Erreur Share of Voice:", error);
    return null;
  }
}
