import { defineEventHandler, getQuery, createError, H3Event } from "h3";

interface ShareOfVoiceResponse {
  data: any;
}

export default defineEventHandler(
  async (event: H3Event): Promise<ShareOfVoiceResponse> => {
    try {
      const config = useRuntimeConfig();

      const baseUrl: string = config.public.PARSER_API_URL;
      const apiKey: string = config.public.PARSER_API;

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

      const brand = String(query.brand || "");
      const brand_report_id = String(query.brand_report_id || "");
      const start_date = query.start_date
        ? String(query.start_date)
        : undefined;
      const end_date = query.end_date ? String(query.end_date) : undefined;
      const model = String(query.model || "all");

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

      const response = await $fetch<ShareOfVoiceResponse>(
        `${baseUrl}/api/report/metrics/share-of-voice`,
        {
          method: "GET",
          query: finalQuery,
          headers: {
            accept: "application/json",
            "X-API-KEY": apiKey,
            "Content-Type": "application/json",
          },
        },
      );

      return response;
    } catch (error: any) {
      const status = error?.statusCode ?? 500;
      const message =
        error?.message ?? "Failed to fetch share of voice metrics";

      throw createError({
        statusCode: status,
        message:
          status >= 400 && status < 500
            ? `Client Error (${status}): ${message}`
            : `Server Error (${status}): ${message}`,
      });
    }
  },
);
