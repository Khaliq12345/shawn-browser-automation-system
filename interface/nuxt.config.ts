import process from "node:process";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  modules: ["@nuxt/ui", "nuxt-charts", "@nuxtjs/mdc"],
  mdc: {
    highlight: {
      highlighter: "shiki",
      theme: {
        default: "github-light",
        dark: "github-dark",
      },
      shikiEngine: "oniguruma",
    },
  },
  css: ["~/assets/css/main.css"],
  runtimeConfig: {
    public: {
      API_URL: process.env.SCRAPER_API_URL,
      PARSER_API_URL: process.env.PARSER_API_URL,
      SCRAPER_API: process.env.SCRAPER_API,
      PARSER_API: process.env.PARSER_API,
    },
  },
  app: {
    head: {
      title: "Brandpeak Dashboard",
      htmlAttrs: {
        lang: "en",
      },
      link: [
        { rel: "icon", type: "image/x-icon", href: "/favicon.ico" },
        {
          rel: "icon",
          type: "image/png",
          sizes: "32x32",
          href: "/favicon-32x32.png",
        },
        {
          rel: "icon",
          type: "image/png",
          sizes: "16x16",
          href: "/favicon-16x16.png",
        },
        {
          rel: "apple-touch-icon",
          sizes: "180x180",
          href: "/apple-touch-icon.png",
        },
      ],
    },
  },
});
