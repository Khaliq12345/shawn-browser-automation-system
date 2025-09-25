export default defineEventHandler(async (event) => {
  const baseUrl = useRuntimeConfig().public.API_URL as string;
  const response = await $fetch(`${event.path}`, {
    baseURL: baseUrl,
    headers: {
      accept: "application/json",
      "X-API-KEY": useRuntimeConfig().public.SCRAPER_API,
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  return response;
});

