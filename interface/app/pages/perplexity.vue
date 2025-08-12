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
                <!-- Last Run Metrics -->
                <div class="mb-10  gap-2 md:gap-5 items-center justify-center text-black">
                    <UCard variant="soft" class="text-center shadow-2xl"
                        :class="iconAndColorFromStatus[last_run.status]['bgColor']">
                        <div class="flex items-center justify-start">
                            <div class="text-left">
                                <div class="flex mb-2">
                                    <UIcon :name="iconAndColorFromStatus[last_run.status]['icon']" size="25"
                                        class="mr-5" />
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
// Last Run of the platform
const last_run: any = {
    status: 'success',
    start_time: '2025-08-12 10:40:56',
    end_time: '2025-08-12 10:47:09',
};
// On Mounted 
onMounted(async () => {
    loadingData.value = true;
    try {
        // Fetch platform data
    } catch (err) {
        console.error('Errors:', err);
    } finally {
        loadingData.value = false;
    }
});
</script>
