export async function getLastRunTimestamp(platform: string): Promise<any> {
  try {
      const response = (await $fetch("/api/metrics/last-run-timestamp", {
        method: "GET",
        params: {
          platform: platform,
        },
      })) as any;
      return response.details;
    } catch (error) {
    console.error("Erreur de requête :", error);
    return null
  }
}