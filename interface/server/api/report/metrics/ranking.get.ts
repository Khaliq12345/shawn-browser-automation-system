import { defineEventHandler, getQuery, createError, H3Event } from "h3";

interface RankingQuery {
  brand: string;
  brand_report_id: string;
  start_date?: string;
  end_date?: string;
  model?: string;
}

export default defineEventHandler(async (event: H3Event): Promise<any> => {
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

    const {
      brand,
      brand_report_id,
      start_date,
      end_date,
      model = "all",
    } = getQuery(event) as RankingQuery;

    if (!brand || !brand_report_id) {
      throw createError({
        statusCode: 422,
        message: "Missing required parameters: brand and brand_report_id",
      });
    }

    const finalQuery: Record<string, string> = {
      brand,
      brand_report_id,
      model,
    };

    if (start_date) finalQuery.start_date = start_date;
    if (end_date) finalQuery.end_date = end_date;

    const response = await $fetch(`${baseUrl}${event.path}`, {
      method: "GET",
      query: finalQuery,
      headers: {
        accept: "application/json",
        "X-API-KEY": apiKey,
        "Content-Type": "application/json",
      },
    });

    return response;
  } catch (error: any) {
    const status = error?.statusCode ?? 500;
    const message = error?.message ?? "Failed to fetch ranking metrics";

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
