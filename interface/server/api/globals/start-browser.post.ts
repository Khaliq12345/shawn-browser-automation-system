export default defineEventHandler(async (event) => {
  const baseUrl = useRuntimeConfig().public.API_URL as string;
  const query = getQuery(event);
  const params = {
    prompt: query.prompt,
    name: query.name,
  };
  const response = await $fetch(`${event.path}`, {
    method: "POST",
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

// "b602ec9374cc1430f10d6db7ad9678b24b72156f28a2b28f9f00103323a25407"
