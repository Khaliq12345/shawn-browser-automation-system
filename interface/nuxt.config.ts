import process from "node:process";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  modules: ["@nuxt/ui"],
  css: ["~/assets/css/main.css"],
  runtimeConfig: {
    public: {
      API_URL: process.env.SCRAPER_API_URL,
      PARSER_API_URL: process.env.PARSER_API_URL,
      SCRAPER_API: process.env.SCRAPER_API,
      PARSER_API: process.env.PARSER_API,
    },
  },
});
