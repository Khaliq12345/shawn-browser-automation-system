export default defineEventHandler(async (event) => {
  const baseUrl = useRuntimeConfig().public.API_URL as string;
  const query = getQuery(event);
  const params = {
    date: query.date,
    platform: query.platform,
  };
  const response = await $fetch(`${event.path}`, {
    baseURL: baseUrl,
    params: params,
  });
  return response;
});
