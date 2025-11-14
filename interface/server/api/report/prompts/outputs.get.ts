export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event);

    const { prompt_id, brand_report_id, date, model, max_date } = query;

    if (!prompt_id || !brand_report_id) {
      throw createError({
        statusCode: 422,
        message: "Missing required parameters: prompt_id and brand_report_id",
      });
    }

    const baseUrl = process.env.PARSER_API_URL;
    const url = `${baseUrl}/api/report/prompts/outputs`;

    const response = await $fetch(url, {
      method: "GET",
      query: {
        prompt_id,
        brand_report_id,
        date,
        model,
        max_date,
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
    throw createError({
      statusCode: 500,
      message: "Unexpected error",
    });
  }
});
