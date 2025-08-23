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
        <!-- Last Run Metrics -->
        <div
          class="mb-10 gap-2 md:gap-5 items-center justify-center text-black"
        >
          <UCard
            variant="soft"
            class="text-center shadow-2xl"
            :class="
              last_run
                ? iconAndColorFromStatus[last_run.status]['bgColor']
                : 'bg-green-200'
            "
          >
            <div class="flex items-center justify-start">
              <div class="text-left">
                <div class="flex mb-2">
                  <UIcon
                    :name="
                      last_run
                        ? iconAndColorFromStatus[last_run.status]['icon']
                        : 'i-heroicons-check'
                    "
                    size="25"
                    class="mr-5"
                  />
                  <p class="font-bold">Last Run Details</p>
                </div>
                <div class="flex justify-center w-full">
                  <USeparator class="my-3 w-full" />
                </div>
                <div v-if="!last_run">Nothing to Show !</div>
                <div v-else class="mb-2" v-for="col in columns">
                  <span class="font-semibold"> {{ col.title }} :</span>
                  <span class="ml-1">
                    {{ last_run[col.key] ?? " - " }}
                  </span>
                </div>
              </div>
            </div>
          </UCard>
        </div>

        <!-- Date -->
        <div class="flex justify-end my-8">
          <UFormField>
            <USelect
              v-model="selectedDate"
              icon="i-heroicons-calendar"
              :items="dateList"
              clearable
              :placeholder="dateList.length ? 'From date' : 'No Available Date'"
              @update:model-value="fetchallData"
            >
            </USelect>
          </UFormField>
        </div>

        <!-- Shared Metrics -->
        <SharedMetrics :platformsMetrics="platformsMetrics" />

        <!-- Logs -->
        <UCollapsible :default-open="false">
          <UButton
            class="w-full p-4 rounded-bl-none rounded-br-none bg-primary-100 hover:bg-primary-200"
          >
            <span class="font-bold text-sm md:text-lg"> Logs </span>
          </UButton>
          <template #content>
            <LogsCard class="w-full" />
          </template>
        </UCollapsible>
      </div>
    </div>
  </NuxtLayout>
</template>

<script lang="ts" setup>
// To Manage Page Loading
const loadingData = ref(false);
// Columns to show
const columns: any[] = [
  {
    title: "Process Id",
    key: "process_id",
  },
  {
    title: "Status",
    key: "status",
  },
  {
    title: "Start Time",
    key: "start_time",
  },
  {
    title: "End Time",
    key: "end_time",
  },
  {
    title: "Prompt",
    key: "prompt",
  },
  {
    title: "Duration (s)",
    key: "duration",
  },
];
// Last Run of the platform
const last_run = ref();
// Routing
const route = useRoute();
const currentPlatform: any = computed(() => route.name);
// On Mounted
onMounted(async () => {
  fetchallData();
});
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
  loadingData.value = true;
  // Last Run Timestamp
  let result = await getLastRunTimestamp(currentPlatform.value);
  last_run.value = result;
  // Job Success Rate
  result = await getJobSuccessRate(selectedDate.value, currentPlatform.value);
  platformsMetrics.find((item) => item.id === 0).data = result;
  // Average Job Duration
  result = await getAverageJobDuration(
    selectedDate.value,
    currentPlatform.value
  );
  platformsMetrics.find((item) => item.id === 1).data = result;
  // Scraper Error Rate
  result = await getScraperErrorRate(selectedDate.value, currentPlatform.value);
  platformsMetrics.find((item) => item.id === 2).data = result;
  loadingData.value = false;
};

// Metrics Functions
//
const {
  getJobSuccessRate,
  getAverageJobDuration,
  getScraperErrorRate,
  getLastRunTimestamp,
} = useMetricsFunctions();

// Shared Metrics Var
//
const { platformsMetrics } = useSharedMetricsVar();
</script>
