export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const baseUrl = useRuntimeConfig().public.API_URL as string;
  const process_id = getRouterParam(event, "process_id");
  const response = await $fetch(`${event.path}`, {
    baseURL: baseUrl,
  });
  return response;
});
