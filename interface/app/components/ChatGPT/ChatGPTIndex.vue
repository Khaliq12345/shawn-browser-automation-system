<template>
  <div class="my-4 text-start ">
    <!-- Last Run Metrics -->
    <div class="mb-10  gap-2 md:gap-5 items-center justify-center text-black">
      <UCard variant="soft" class="text-center shadow-2xl" :class="iconAndColorFromStatus[last_run.status]['bgColor']">
        <div class="flex items-center justify-start">
          <div class="text-left">
            <div class="flex mb-2">
              <UIcon :name="iconAndColorFromStatus[last_run.status]['icon']" size="25" class="mr-5" />
              <p class="font-bold">Last Run</p>
            </div>
            <div class="flex justify-center">
              <USeparator class="my-3" />
            </div>
            <div class="mb-2" v-for="col in columns">
              <span class="font-semibold"> {{ col.title }} :</span>
              <span class="ml-1">
                {{ last_run[col.key] }}
              </span>
            </div>
          </div>
        </div>
      </UCard>
    </div>
    <!-- Logs -->
    <UCollapsible :default-open="false">
      <UButton class="w-full p-4 rounded-bl-none rounded-br-none bg-primary-100 hover:bg-primary-200">
        <span class="font-bold text-sm md:text-lg"> Logs </span>
      </UButton>
      <template #content>
        <LogsCard class="w-full" />
      </template>
    </UCollapsible>
  </div>
</template>


<script setup lang="ts">

import { iconAndColorFromStatus } from '~/utils/globals';

const columns: any[] = [
  {
    title: "Last Run Status",
    key: "status",
  },
  {
    title: "Last Run Start",
    key: "start_time",
  },
  {
    title: "Last Run End",
    key: "end_time",
  },
]

const last_run: any = {
  status: 'success',
  start_time: '2025-08-12 10:40:56',
  end_time: '2025-08-12 10:47:09',
};


</script>
