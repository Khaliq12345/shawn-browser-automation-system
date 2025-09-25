export default defineEventHandler(async (event) => {
  const baseUrl = useRuntimeConfig().public.API_URL as string;
  const query = getQuery(event);
  const params = {
    platform: query.platform,
  };
  const response = await $fetch(`${event.path}`, {
    baseURL: baseUrl,
    params: params,
    headers: {
      accept: "application/json",
      "X-API-KEY": useRuntimeConfig().public.SCRAPER_API,
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  return response;
});
