<template>
    <UProgress v-if="loading" animation="swing" />
    <div class="grid grid-cols-2 m-2">
        <UCard v-for="data in reports" variant="soft" class="m-10">
            <div class="space-4 text-sm">
                <div>
                    <span class="font-medium text-gray-600 dark:text-gray-400"
                        >Prompt ID:</span
                    >
                    <span class="ml-2 text-gray-900 dark:text-white">{{
                        data.prompt_id
                    }}</span>
                </div>

                <div>
                    <span class="font-medium text-gray-600 dark:text-gray-400"
                        >Brand Report ID:</span
                    >
                    <span class="ml-2 text-gray-900 dark:text-white">{{
                        data.brand_report_id
                    }}</span>
                </div>

                <div>
                    <span class="font-medium text-gray-600 dark:text-gray-400"
                        >Prompt:</span
                    >
                    <p class="mt-1 text-gray-900 dark:text-white italic">
                        {{ data.prompt }}
                    </p>
                </div>
            </div>

            <template #footer>
                <div class="pt-2 border-t border-gray-200 dark:border-gray-700">
                    <div class="flex justify-between">
                        <span
                            class="font-medium text-gray-600 dark:text-gray-400"
                            >Last Run:</span
                        >
                        <span class="text-gray-900 dark:text-white">{{
                            formatDate(data.last_run)
                        }}</span>
                    </div>
                    <div class="flex justify-between mt-2">
                        <span
                            class="font-medium text-gray-600 dark:text-gray-400"
                            >Next Run:</span
                        >
                        <span class="text-gray-900 dark:text-white">{{
                            formatDate(data.next_run)
                        }}</span>
                    </div>
                    <UButton
                        trailing-icon="i-lucide-arrow-right"
                        size="md"
                        color="secondary"
                        class="m-5"
                        :to="`/report-details/${data.brand_report_id}`"
                        >Go to Report</UButton
                    >
                </div>
            </template>
        </UCard>
    </div>

    <div class="flex justify-center mt-10">
        <UFieldGroup class="space-x-7">
            <UButton
                color="neutral"
                variant="subtle"
                icon="i-lucide-chevron-left"
                @click="onButtonClick('prev')"
            />
            <UButton
                color="neutral"
                variant="outline"
                icon="i-lucide-chevron-right"
                @click="onButtonClick('next')"
            />
        </UFieldGroup>
    </div>
</template>

<script setup>
const reports = ref();
const loading = ref(false);
let page = ref(1);
const limit = ref(10);

const onButtonClick = async (action) => {
    if (action == "prev") {
        page.value = page.value - 1;
    } else if (action == "next") {
        page.value = page.value + 1;
    }
    await loadData();
};

onMounted(async () => {
    await loadData();
});

const loadData = async () => {
    loading.value = true;
    reports.value = [];
    try {
        const response = await getSchedule(limit.value, page.value);
        reports.value = response;
        console.log(response);
    } catch (err) {
        console.log(err);
    } finally {
        loading.value = false;
    }
};

// Format ISO dates to readable format
const formatDate = (isoString) => {
    if (!isoString) return "N/A";
    return new Date(isoString).toLocaleString("en-US", {
        dateStyle: "medium",
        timeStyle: "medium",
    });
};
</script>
