import { defineEventHandler, getQuery, createError, H3Event } from "h3";

export default defineEventHandler(async (event: H3Event) => {
  try {
    const config = useRuntimeConfig();

    const baseUrl = config.public.PARSER_API_URL;
    const apiKey = config.public.PARSER_API;

    if (!baseUrl) {
      throw createError({
        statusCode: 500,
        message: "PARSER_API_URL is not defined",
      });
    }

    if (!apiKey) {
      throw createError({
        statusCode: 500,
        message: "PARSER_API key is not defined",
      });
    }

    const query = getQuery(event);

    const brand_report_id = String(query.brand_report_id || "");
    const date = query.date ? String(query.date) : undefined;
    const model = query.model ? String(query.model) : "all";

    if (!brand_report_id) {
      throw createError({
        statusCode: 422,
        message: "Missing required parameter: brand_report_id",
      });
    }

    const url = `${baseUrl}/api/report/prompts/citations`;

    const response = await $fetch(url, {
      method: "GET",
      query: {
        brand_report_id,
        date,
        model,
      },
    });
    return response;
  } catch (err: any) {
    const status = err?.statusCode || err?.status || 500;
    const message = err?.message || "Unknown error";

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
    throw createError({ statusCode: 500, message: "Unexpected error" });
  }
});
