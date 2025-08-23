export const platformsMetrics: any[] = [
    {
      id: 0,
      title: "Job Success Rate",
      color: "bg-green-200",
      columns: [
        {
          title: "Total Jobs",
          key: "total_jobs",
        },
        {
          title: "Sucess Jobs",
          key: "success_jobs",
        },
        {
          title: "Sucess Rate (%)",
          key: "success_rate",
        },
      ],
    },
    {
      id: 1,
      title: "Average Job Duration",
      color: "bg-cyan-200",
      columns: [
        {
          title: "Total Jobs",
          key: "total_jobs",
        },
        {
          title: "Average Duration (s)",
          key: "average_duration_seconds",
        },
      ],
    },
    {
      id: 2,
      title: "Scraper Error Rate",
      color: "bg-red-200",
      columns: [
        {
          title: "Total Jobs",
          key: "total_jobs",
        },
        {
          title: "Failed Jobs",
          key: "failed_jobs",
        },
        {
          title: "Failed Rate (%)",
          key: "failed_rate",
        },
      ],
    },
  ];