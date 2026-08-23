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
export async function getReportCitations({
  brand_report_id,
  date = null,
  model = "all",
}: {
  brand_report_id: string;
  date?: string | null;
  model?: string;
}): Promise<string | null> {
  try {
    const response = (await $fetch("/api/report/prompts/citations", {
      method: "GET",
      params: {
        brand_report_id,
        date,
        model,
      },
    })) as string;

    return response;
  } catch (error) {
    console.error("Erreur de requête citations :", error);
    return null;
  }
}
