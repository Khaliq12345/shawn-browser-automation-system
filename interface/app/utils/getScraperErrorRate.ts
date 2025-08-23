export async function getScraperErrorRate(date: string, platform: string): Promise<any> {
  try {
      const response = (await $fetch("/api/metrics/scraper-error-rate", {
        method: "GET",
        params: {
          date: date,
          platform: platform,
        },
      })) as any;
      return response.details;
    } catch (error) {
    console.error("Erreur de requête :", error);
    return null
  }
}