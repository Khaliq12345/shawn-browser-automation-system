export async function getAverageTotalTimePerPrompt(date: string): Promise<any> {
  try {
      const response = (await $fetch(
        "/api/metrics/average-total-time-per-prompt",
        {
          method: "GET",
          params: {
            date: date,
          },
        }
      )) as any;
      return response.details as Array<any>;
    } catch (error) {
    console.error("Erreur de requête :", error);
    return null
  }
}