export async function getReportPromptOutput({
  prompt_id,
  brand_report_id,
  date = null,
  model = "chatgpt",
  max_date = "7 days ago",
}: {
  prompt_id: string;
  brand_report_id: string;
  date?: string | null;
  model?: string;
  max_date?: string;
}): Promise<any> {
  try {
    const response = (await $fetch("/api/report/prompts/outputs", {
      method: "GET",
      params: {
        prompt_id,
        brand_report_id,
        date,
        model,
        max_date,
      },
    })) as any;

    return response.details as Array<any>;
  } catch (error) {
    console.error("Erreur de requête :", error);
    return null;
  }
}
