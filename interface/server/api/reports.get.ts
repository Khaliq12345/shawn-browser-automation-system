import { defineEventHandler, getQuery, createError, H3Event } from "h3";

export default defineEventHandler(async (event: H3Event): Promise<any> => {
  try {
    const config = useRuntimeConfig();

    const baseUrl = useRuntimeConfig().public.API_URL as string;
    const query = getQuery(event);

    const params = {
      limit: String(query.limit ?? "20"),
      page: String(query.page ?? "1"),
    };

    const response = await $fetch("/api/reports/", {
      baseURL: baseUrl,
      method: "GET",
      query: params,
      headers: {
        accept: "application/json",
        "X-API-KEY": useRuntimeConfig().public.SCRAPER_API,
        "Content-Type": "application/json",
      },
    });

    return response;
  } catch (err: any) {
    console.error("Error in reports.get.ts:", err);
    throw createError({
      statusCode: err?.statusCode || 500,
      message: err?.message || "Failed to fetch /api/reports",
    });
  }
});
