import { defineEventHandler, getQuery, createError, H3Event } from "h3";

interface PromptOutputsResponse {
  data: any; // Ajuste selon ta vraie structure
}

export default defineEventHandler(
  async (event: H3Event): Promise<PromptOutputsResponse> => {
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

      const prompt_id = String(query.prompt_id || "");
      const brand_report_id = String(query.brand_report_id || "");
      const date = query.date ? String(query.date) : undefined;
      const model = query.model ? String(query.model) : "chatgpt"; // Valeur par défaut
      const max_date = query.max_date ? String(query.max_date) : "7 days ago"; // Valeur par défaut

      if (!prompt_id || !brand_report_id) {
        throw createError({
          statusCode: 422,
          message: "Missing required parameters: prompt_id and brand_report_id",
        });
      }

      // Construire les params dynamiquement
      const params: Record<string, string> = {
        prompt_id,
        brand_report_id,
        model,
        max_date,
      };

      if (date) params.date = date;

      // Faire la requête externe avec clé API dans header
      const response = await $fetch<PromptOutputsResponse>(
        `${baseUrl}/api/report/prompts/outputs`,
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
  },
);
