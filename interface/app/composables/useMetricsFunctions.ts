export function useMetricsFunctions() {
  // Metrics Functions
  //
  // Job Success Rate
  const getJobSuccessRate = async (date: string, platform: string) => {
    try {
      const response = (await $fetch("/api/metrics/job-success-rate", {
        method: "GET",
        params: {
          date: date,
          platform: platform,
        },
      })) as any;
      return response.details;
    } catch (error) {
      console.error("Erreur de requete:", error);
    }
  };

  // Average Job Duration
  const getAverageJobDuration = async (date: string, platform: string) => {
    try {
      const response = (await $fetch("/api/metrics/average-job-duration", {
        method: "GET",
        params: {
          date: date,
          platform: platform,
        },
      })) as any;
      return response.details;
    } catch (error) {
      console.error("Erreur de requete:", error);
    }
  };

  // Scraper Error Rate
  const getScraperErrorRate = async (date: string, platform: string) => {
    try {
      const response = (await $fetch("/api/metrics/scraper-error-rate", {
        method: "GET",
        params: {
          date: date,
          platform: platform,
        },
      })) as any;
      return response.details;
    } catch (error) {
      console.error("Erreur de requete:", error);
    }
  };

  // Prompt Coverage Rate
  const getPromptCoverageRate = async (date: string) => {
    try {
      const response = (await $fetch("/api/metrics/prompt-coverage-rate", {
        method: "GET",
        params: {
          date: date,
        },
      })) as any;
      return response.details as Array<any>;
    } catch (error) {
      console.error("Erreur de requete:", error);
    }
  };

  // Average Total Time Per Prompt
  const getAverageTotalTimePerPrompt = async (date: string) => {
    try {
      const response = (await $fetch(
        "/api/metrics/average-total-time-per-prompt",
        {
          method: "GET",
          params: {
            date: date,
          },
        }
      )) as any;
      return response.details as Array<any>;
    } catch (error) {
      console.error("Erreur de requete:", error);
    }
  };

  // Last Run Timestamp
  const getLastRunTimestamp = async (platform: string) => {
    try {
      const response = (await $fetch("/api/metrics/last-run-timestamp", {
        method: "GET",
        params: {
          platform: platform,
        },
      })) as any;
      return response.details;
    } catch (error) {
      console.error("Erreur de requete:", error);
    }
  };

  return {
    getJobSuccessRate,
    getAverageJobDuration,
    getScraperErrorRate,
    getPromptCoverageRate,
    getAverageTotalTimePerPrompt,
    getLastRunTimestamp,
  };
}
