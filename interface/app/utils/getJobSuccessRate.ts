export async function getJobSuccessRate(date: string, platform: string): Promise<any> {
  try {
    const response = await $fetch("/api/metrics/job-success-rate", {
      method: "GET",
      params: {
        date,
        platform,
      },
    });
    return (response as any).details;
  } catch (error) {
    console.error("Erreur de requête :", error);
    return null
  }
}