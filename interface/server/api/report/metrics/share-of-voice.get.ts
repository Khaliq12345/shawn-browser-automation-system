export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event);
    const {
      brand,
      brand_report_id,
      start_date,
      end_date,
      model = "all",
    } = query;

    if (!brand || !brand_report_id) {
      throw createError({
        statusCode: 422,
        message: "Missing required parameters: brand and brand_report_id",
      });
    }

    const baseUrl = process.env.PARSER_API_URL;
    const url = `${baseUrl}/api/report/metrics/share-of-voice`;

    const response = await $fetch(url, {
      method: "GET",
      query: {
        brand,
        brand_report_id,
        start_date,
        end_date,
        model,
      },
    });

    return response;
  } catch (error: any) {
    const status = error?.statusCode ?? 500;
    const message = error?.message ?? "Failed to fetch share of voice metrics";

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
