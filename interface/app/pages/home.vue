<template>
  <NuxtLayout name="default">
    <div
      v-if="loadingData"
      class="place-items-center place-content-center my-15"
    >
      <UProgress animation="swing" color="neutral" />
      <div class="container mx-auto p-4 text-center">
        <p>Loading Data ...</p>
      </div>
    </div>
    <!-- When Loaded -->
    <div v-else>
      <div class="my-4 text-start">
        <!-- Date -->
        <div class="flex justify-end my-8">
          <USelect
            v-model="selectedDate"
            icon="i-heroicons-calendar"
            :items="dateList"
            clearable
            :placeholder="dateList.length ? 'From date' : 'No Available Date'"
            @update:model-value="fetchallData"
          >
          </USelect>
        </div>

        <!-- Shared Metrics -->
        <SharedMetrics :platforms-metrics="platformsMetrics" />

        <!-- Like Table Metrics -->
        <div
          class="grid grid-cols-1 gap-5 items-center justify-center text-black"
          v-for="item in platformLikeTableMetrics"
        >
          <UCard
            variant="solid"
            class="text-center shadow-2xl p-0 mb-10"
            :class="item.color"
          >
            <div class="flex items-center justify-center w-full">
              <div class="text-left">
                <div class="flex mb-2 justify-center">
                  <p class="font-bold text-xl">{{ item.title }}</p>
                </div>
                <div class="flex justify-center w-full">
                  <USeparator class="my-3 w-full" />
                </div>
                <div v-if="!item.data">Nothing to Show !</div>
                <div v-else class="m-2">
                  <TableModel
                    :columns0="item.cols"
                    :data0="item.data"
                    :key="item.title"
                  />
                </div>
              </div>
            </div>
          </UCard>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script lang="ts" setup>
// Platform Metrics
const { platformsMetrics } = usePlateformMetrics();
// Average Total Time Per Prompt
const averageTTPPData = ref();
const averageTTPPcols: string[] = [
  "prompt",
  "total_jobs",
  "average_total_time_seconds",
];
const averageTTPPcolumns: any = [];
averageTTPPcols.forEach((col) => {
  let keyName = "";
  let cell = "";
  keyName = col.replaceAll("_", " ").toUpperCase();
  cell = "";
  averageTTPPcolumns.push({
    accessorKey: col,
    header: keyName,
    cell: ({ row }: any) => `${cell}${formatValue(row.getValue(col))}`,
    meta: {
      class: {
        th: "font-bold text-center",
        td: "text-black font-semibold",
      },
    },
  });
});
// Prompt Coverage Rate
const promptCRateData = ref();
const promptCRatecols: string[] = ["total"];
const promptCRatecolumns: any = [];
promptCRatecols.forEach((col, i) => {
  let keyName = "";
  let cell = "";
  keyName = col.replaceAll("_", " ").toUpperCase();
  cell = "";
  promptCRatecolumns.push({
    accessorKey: col,
    header: keyName,
    cell: ({ row }: any) => `${cell}${formatValue(row.getValue(col))}`,
    meta: {
      class: {
        th: "font-bold text-center",
        td: "text-black font-semibold",
      },
    },
  });
});
// For Showing Overall Metrics as Table
const platformLikeTableMetrics: any[] = [
  {
    title: "Average Total Time Per Prompt",
    data: averageTTPPData,
    cols: averageTTPPcolumns,
    color: "bg-amber-200",
  },
];
//
// To Manage Page Loading
const loadingData = ref(false);
// Dates
const dateList = ref([
  "24 hours ago",
  "1 week ago",
  "1 month ago",
  "1 year ago",
]);
const selectedDate: Ref<any> = ref(dateList.value[0]);
// Fetch All Data
//
const fetchallData = async () => {
  try {
    loadingData.value = true;
    // Job Success Rate
    let result = await getJobSuccessRate(selectedDate.value, "all");
    platformsMetrics.value.find((item) => item.id === 0).data = result;
    // Average Job Duration
    result = await getAverageJobDuration(selectedDate.value, "all");
    platformsMetrics.value.find((item) => item.id === 1).data = result;
    // Scraper Error Rate
    result = await getScraperErrorRate(selectedDate.value, "all");
    platformsMetrics.value.find((item) => item.id === 2).data = result;
    // Total Running Jobs
    result = await getTotalRunningJobs(selectedDate.value, "all");
    platformsMetrics.value.find((item) => item.id === 3).data = result;
    // Average Total Time Per Prompt
    result = await getAverageTotalTimePerPrompt(selectedDate.value);
    averageTTPPData.value = result;
  } catch (error) {
    console.log(`Requests error - ${error}`);
  } finally {
    loadingData.value = false;
  }
};
// On Mounted
onMounted(async () => {
  await fetchallData();
});
</script>
