<template>
  <div>
    <!-- General Metrics -->
    <div
      class="mb-10 grid grid-cols-1 lg:grid-cols-3 gap-2 md:gap-5 items-center justify-center text-black"
    >
      <div class="" v-for="item in platformsMetrics">
        <UCard
          variant="soft"
          class="text-center shadow-2xl p-0"
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
              <div v-else class="mb-2" v-for="col in item.columns">
                <span class="font-semibold"> {{ col.title }} :</span>
                <span class="ml-1">
                  {{ formatValue(item.data[col.key]) }}
                </span>
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// For Showing Overall Metrics
const props = defineProps({
  platformsMetrics: Array<any>,
});
</script>
