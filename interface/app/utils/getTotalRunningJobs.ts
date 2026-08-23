export async function getTotalRunningJobs(date: string, platform: string): Promise<any> {
  try {
      const response = (await $fetch("/api/metrics/total-running-jobs", {
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