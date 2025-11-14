export async function getCitations(params: {
  brand_report_id: string;
  date?: string | null;
  model?: string;
}): Promise<any> {
  try {
    return await $fetch("/api/report/prompts/citations", {
      method: "GET",
      params,
    });
  } catch (error) {
    console.error("Erreur Citations:", error);
    return null;
  }
}
