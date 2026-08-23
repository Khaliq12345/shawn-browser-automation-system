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

    // Construire proprement la query sans paramètres vides
    const fetchQuery: Record<string, string> = {
      brand_report_id,
      model,
    };
    if (date && date.trim() !== "") {
      fetchQuery.date = date;
    }

    const response = await $fetch(url, {
      method: "GET",
      query: fetchQuery,
      headers: {
        "X-API-KEY": apiKey, // N'oublie pas d'ajouter l'API key ici
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
