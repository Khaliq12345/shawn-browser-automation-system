<template>
  <NuxtLayout name="default">
    <div v-if="loadingData" class="place-items-center place-content-center my-15">
      <UProgress animation="swing" color="neutral" />
      <div class="container mx-auto p-4 text-center">
        <p>Loading Data ...</p>
      </div>
    </div>
    <!-- When Loaded -->
    <div v-else>
      <div class="my-4 text-start ">
        <!-- General Metrics -->
        <div class="mb-10 grid grid-cols-1 lg:grid-cols-3 gap-2 md:gap-5 items-center justify-center text-black">
          <div class="" v-for="item in platformsMetrics">
            <UCard variant="soft" class="text-center shadow-2xl"
              :class="iconAndColorFromStatus[item.last_run_status]['bgColor']">
              <div class="flex items-center justify-start">
                <div class="text-left">
                  <div class="flex mb-2">
                    <UIcon :name="iconAndColorFromStatus[item.last_run_status]['icon']" size="25" class="mr-5" />
                    <p class="font-bold">{{ item.title }}</p>
                  </div>
                  <div class="mb-2" v-for="col in columns">
                    <span class="font-semibold"> {{ col.title }} :</span>
                    <span class="ml-1">
                      {{ item[col.key] }}
                    </span>
                  </div>
                </div>
              </div>
            </UCard>
          </div>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script lang="ts" setup>
import { iconAndColorFromStatus } from '~/utils/globals';
// To Manage Page Loading
const loadingData = ref(false);
// Columns to show
const columns: any[] = [
  {
    title: "Sucessful Runs",
    key: "success",
  },
  {
    title: "Failed Runs",
    key: "failled",
  },
  {
    title: "Last Run Status",
    key: "last_run_status",
  },
]
// For Showing Overall Metrics
const platformsMetrics: any[] = [
  {
    title: "Chat GPT",
    success: 3,
    failled: 7,
    total: 10,
    last_run_status: 'success',
  },
  {
    title: "Perplexity",
    success: 3,
    failled: 0,
    total: 4,
    last_run_status: 'running',
  },
  {
    title: "Gemini",
    success: 2,
    failled: 1,
    total: 3,
    last_run_status: 'error',
  },
];
// On Mounted 
onMounted(async () => {
  loadingData.value = true;
  try {
    // Fetch home data
  } catch (err) {
    console.error('Errors:', err);
  } finally {
    loadingData.value = false;
  }
});
</script>
