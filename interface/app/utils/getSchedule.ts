export async function getSchedule(limit: number, page: number): Promise<any> {
  try {
    const response = (await $fetch("/api/schedule/", {
      method: "GET",
      params: {
        limit: limit,
        page: page,
      },
    })) as any;
    return response;
  } catch (error) {
    console.error("Erreur de requête :", error);
    return null;
  }
}
