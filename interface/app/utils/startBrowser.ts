export async function startBrowser(prompt: string, name: string): Promise<any> {
  try {
    const response = await $fetch("/api/globals/start-browser", {
      method: "POST",
      params: {
        prompt,
        name,
      },
    });
    return (response as any).details;
  } catch (error) {
    console.error("Erreur de requête :", error);
    return null;
  }
}
