import { defineEventHandler, getQuery, createError, H3Event } from "h3";

export default defineEventHandler(async (event: H3Event): Promise<any> => {
  try {
    const config = useRuntimeConfig();

    const baseUrl = config.public.PARSER_API_URL;
    const apiKey = config.public.PARSER_API;

    if (!apiKey) {
      throw createError({
        statusCode: 500,
        message: "PARSER_API key is not defined in runtime config",
      });
    }

    const query = getQuery(event);

    const brand_report_id = query.brand_report_id ? String(query.brand_report_id) : undefined;
    const limit = query.limit ? Number(query.limit) : undefined;
    const page = query.page ? Number(query.page) : undefined;

    if (!brand_report_id) {
      throw createError({
        statusCode: 422,
        message: "Missing required parameter: brand_report_id",
      });
    }

    const params: Record<string, string | number> = {
      brand_report_id,
    };

    if (limit) params.limit = limit;
    if (page) params.page = page;

    const response = await $fetch<any>(
      `${baseUrl}/api/report/prompts/reports`,
      {
        method: "GET",
        query: params,
        headers: {
          accept: "application/json",
          "X-API-KEY": apiKey,
        },
      },
    );

    return response;

  } catch (err: any) {
    const status = err?.statusCode || err?.status || 500;
    const message = err?.message || "Unknown error";

    console.error(`Error fetching reports: ${message}`, err);

    if (status >= 400 && status < 500) {
      throw createError({
        statusCode: status,
        message: `Client Error (${status}): ${message}`,
      });
    }
    if (status >= 500 && status < 600) {
      throw createError({
        statusCode: status,
        message: `Server Error (${status}): ${message}`,
      });
    }
    throw createError({
      statusCode: 500,
      message: "Unexpected error",
    });
  }
});
