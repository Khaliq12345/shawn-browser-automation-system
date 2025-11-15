export async function getSentiments(params: {
  brand_report_id: string;
  date?: string | null;
  model?: string;
}): Promise<any> {
  try {
    return await $fetch("/api/report/prompts/sentiments", {
      method: "GET",
      params,
    });
  } catch (error) {
    console.error("Erreur Sentiments:", error);
    return null;
  }
}
