export async function getPromptCoverageRate(date: string): Promise<any> {
  try {
      const response = (await $fetch("/api/metrics/prompt-coverage-rate", {
        method: "GET",
        params: {
          date: date,
        },
      })) as any;
      return response.details as Array<any>;
    } catch (error) {
    console.error("Erreur de requête :", error);
    return null
  }
}