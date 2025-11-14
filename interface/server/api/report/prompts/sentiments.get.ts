export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event);
    const { brand_report_id, date = null, model = "all" } = query;

    if (!brand_report_id) {
      throw createError({
        statusCode: 422,
        message: "Missing required parameter: brand_report_id",
      });
    }

    const baseUrl = process.env.PARSER_API_URL;
    const url = `${baseUrl}/api/report/prompts/sentiments`;

    const response = await $fetch(url, {
      method: "GET",
      query: {
        brand_report_id,
        date,
        model,
      },
    });

    return response;
  } catch (error: any) {
    const status = error?.statusCode ?? 500;
    const message = error?.message ?? "Failed to fetch sentiments";

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
