<template>
    <UProgress v-if="loading" animation="swing" size="sm" />

    <UContainer class="py-8">
        <div class="flex items-center justify-between mb-6 mx-2">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                Report Outputs
            </h1>
            <UBadge variant="subtle" size="lg">ID: {{ brandReportId }}</UBadge>
        </div>

        <!-- Message si vide -->
        <div
            v-if="!loading && (!outputs || outputs.length === 0)"
            class="text-center py-12 text-gray-500"
        >
            No outputs found for this report.
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6 m-2">
            <UCard
                v-for="data in outputs"
                :key="data.id"
                variant="soft"
                class="transition-shadow hover:shadow-md"
            >
                <div class="space-y-4 text-sm">
                    <!-- Model -->
                    <div>
                        <span
                            class="font-medium text-gray-600 dark:text-gray-400"
                            >Model:</span
                        >
                        <p
                            class="mt-1 text-lg font-semibold text-gray-900 dark:text-white capitalize"
                        >
                            {{ data.model }}
                        </p>
                    </div>

                    <!-- Prompt ID -->
                    <div class="flex items-center">
                        <span
                            class="font-medium text-gray-600 dark:text-gray-400 min-w-[120px]"
                            >Prompt ID:</span
                        >
                        <span
                            class="ml-2 text-gray-900 dark:text-white truncate"
                            >{{ data.prompt_id }}</span
                        >
                    </div>

                    <!-- Brand Report ID -->
                    <div class="flex items-center">
                        <span
                            class="font-medium text-gray-600 dark:text-gray-400 min-w-[120px]"
                            >Brand Report ID:</span
                        >
                        <span
                            class="ml-2 text-gray-900 dark:text-white truncate"
                            >{{ data.brand_report_id }}</span
                        >
                    </div>
                </div>

                <!-- Footer avec Date et Bouton -->
                <template #footer>
                    <div
                        class="pt-4 border-t border-gray-200 dark:border-gray-700"
                    >
                        <div class="flex justify-between items-center mb-4">
                            <span
                                class="font-medium text-gray-600 dark:text-gray-400"
                                >Date:</span
                            >
                            <span
                                class="text-gray-900 dark:text-white font-mono text-xs"
                            >
                                {{ formatDate(data.date) }}
                            </span>
                        </div>

                        <UButton
                            block
                            trailing-icon="i-heroicons-arrow-right"
                            size="md"
                            color="secondary"
                            variant="solid"
                            @click="showOutput(data)"
                        >
                            Show output
                        </UButton>
                    </div>
                </template>
            </UCard>
        </div>

        <!-- Pagination -->
        <div class="flex justify-center mt-10 space-x-7">
            <UButton
                color="secondary"
                variant="ghost"
                icon="i-heroicons-chevron-left"
                :disabled="page <= 1 || loading"
                @click="onButtonClick('prev')"
            />

            <span class="flex items-center text-sm text-gray-500"
                >Page {{ page }}</span
            >

            <UButton
                color="secondary"
                variant="ghost"
                icon="i-heroicons-chevron-right"
                :disabled="(outputs?.length || 0) < limit || loading"
                @click="onButtonClick('next')"
            />
        </div>
    </UContainer>
</template>

<script setup lang="ts">
import type { ReportItem } from "../../../types/report";

const route = useRoute();
const brandReportId = String(route.params.id);

// State
const page = ref(1);
const limit = 10;
const outputs = ref<ReportItem[]>([]);
const loading = ref(false);

const buildQuery = () => ({
    brand_report_id: brandReportId,
    page: page.value,
    limit,
});

const fetchOutputs = async () => {
    loading.value = true;
    try {
        const data = await $fetch<ReportItem[]>("/api/report/prompts/reports", {
            query: buildQuery(),
        });
        outputs.value = Array.isArray(data) ? data : [];
    } catch (error) {
        console.error("Failed to fetch report outputs:", error);
        outputs.value = [];
    } finally {
        loading.value = false;
    }
};

watch(page, () => {
    fetchOutputs();
});

onMounted(() => {
    fetchOutputs();
});

// Gestion des clics de pagination
const onButtonClick = (action: "prev" | "next") => {
    if (action === "prev" && page.value > 1) {
        page.value--;
    } else if (action === "next") {
        page.value++;
    }
};

// Navigation
const showOutput = (data: ReportItem) => {
    navigateTo({
        path: `/report/${brandReportId}/show`,
        query: {
            prompt_id: data.prompt_id,
            model: data.model,
            date: data.date,
            brand_report_id: data.brand_report_id,
        },
    });
};

// Format ISO dates to readable format
const formatDate = (dateStr: string) => {
    if (!dateStr) return "N/A";

    return new Date(dateStr).toLocaleString("en-US", {
        dateStyle: "medium",
        timeStyle: "short",
    });
};
</script>
