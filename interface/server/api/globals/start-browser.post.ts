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
  });
  return response;
});
