<template>
    <UContainer class="py-8 space-y-6">
        <div class="flex items-center justify-between">
            <h1 class="text-2xl font-bold">Brand Metrics</h1>
            <UBadge variant="subtle" size="lg" color="secondary"
                >Report ID: {{ brandReportId }}</UBadge
            >
        </div>

        <UCard>
            <template #header>
                <div class="font-semibold">Configuration</div>
            </template>

            <div
                class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 items-end"
            >
                <UFormField label="Brand Name *">
                    <UInput
                        v-model="form.brand"
                        placeholder="ex: Nike"
                        icon="i-heroicons-tag"
                    />
                </UFormField>

                <UFormField label="Model">
                    <USelect
                        v-model="form.model"
                        :options="modelOptions"
                        option-attribute="label"
                    />
                </UFormField>

                <UFormField label="Start Date">
                    <UInput v-model="form.start_date" type="date" />
                </UFormField>

                <UFormField label="End Date">
                    <UInput v-model="form.end_date" type="date" />
                </UFormField>

                <UButton
                    block
                    size="md"
                    color="secondary"
                    variant="solid"
                    label="Refresh Data"
                    :loading="loading"
                    :disabled="!form.brand"
                    icon="i-heroicons-arrow-path"
                    @click="refreshAllMetrics"
                />
            </div>
        </UCard>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <UCard
                v-for="metric in metricsConfig"
                :key="metric.key"
                :class="[
                    'flex flex-col h-full',
                    metric.fullWidth ? 'md:col-span-2' : '',
                ]"
            >
                <template #header>
                    <div
                        class="flex items-center gap-2 font-semibold text-gray-800 dark:text-gray-100"
                    >
                        <UIcon :name="metric.icon" class="w-5 h-5" />
                        <span>{{ metric.title }}</span>
                    </div>
                </template>

                <div v-if="loading" class="space-y-2 animate-pulse">
                    <div
                        class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"
                    ></div>
                    <div
                        class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"
                    ></div>
                </div>

                <template v-else>
                    <p
                        v-if="!results[metric.key]"
                        class="text-gray-400 italic text-sm"
                    >
                        No data available. Click refresh.
                    </p>

                    <div v-else class="max-h-64 overflow-auto space-y-3">
                        <template v-if="metric.key === 'ranking'">
                            <div
                                v-if="
                                    getRankingEntries(results[metric.key])
                                        .length
                                "
                                class="space-y-2"
                            >
                                <div
                                    v-for="(row, idx) in getRankingEntries(
                                        results[metric.key],
                                    )"
                                    :key="idx"
                                    class="flex flex-wrap items-center gap-2 rounded border border-gray-200 dark:border-gray-800 p-3 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 transition"
                                >
                                    <UBadge
                                        color="success"
                                        variant="soft"
                                        size="xs"
                                        >#{{ row.rank ?? "—" }}</UBadge
                                    >
                                    <span class="flex-1 font-medium truncate">{{
                                        row.brand_name ?? "Unknown"
                                    }}</span>
                                    <span class="text-xs text-gray-500"
                                        >Mentions:
                                        {{ row.mention_count ?? 0 }}</span
                                    >
                                </div>
                            </div>
                            <p v-else class="text-gray-400 italic text-sm">
                                No ranking data found.
                            </p>
                        </template>

                        <template v-else>
                            <dl class="space-y-2 text-sm">
                                <template
                                    v-for="(item, idx) in normalizeData(
                                        results[metric.key],
                                    )"
                                    :key="idx"
                                >
                                    <div
                                        class="flex justify-between items-center py-1 border-b border-gray-100 dark:border-gray-800 last:border-0"
                                    >
                                        <dt
                                            class="text-gray-500 font-medium capitalize"
                                        >
                                            {{ item.label }}
                                        </dt>
                                        <dd
                                            class="font-bold text-gray-900 dark:text-white"
                                        >
                                            {{ item.value }}
                                        </dd>
                                    </div>
                                </template>
                            </dl>
                        </template>
                    </div>
                </template>
            </UCard>
        </div>

        <UCard v-if="form.brand" class="md:col-span-2">
            <template #header>
                <div
                    class="flex items-center gap-2 font-semibold text-gray-800 dark:text-gray-100"
                >
                    <UIcon name="i-heroicons-chart-bar" class="w-5 h-5" />
                    <span>Ranking Over Time</span>
                </div>
            </template>
            <ClientOnly>
                <RankOverTime
                    :brand="form.brand"
                    :brand-report-id="brandReportId"
                    :model="form.model"
                    :start-date="form.start_date"
                    :end-date="form.end_date"
                />
            </ClientOnly>
        </UCard>
    </UContainer>
</template>

<script setup lang="ts">
import RankOverTime from "~/components/metrics/RankOverTime.vue";
import type { MetricConfig, MetricKey, RankingEntry } from "~/types/metrics";

const route = useRoute();
const toast = useToast();
const brandReportId = String(route.params.id);
const loading = ref(false);

const modelOptions = [
    { label: "All Models", value: "all" },
    { label: "ChatGPT", value: "chatgpt" },
    { label: "Perplexity", value: "perplexity" },
    { label: "Claude", value: "claude" },
    { label: "Google", value: "google" },
];

const form = reactive({
    brand: "",
    model: "all",
    start_date: undefined as string | undefined,
    end_date: undefined as string | undefined,
});

const results = reactive<Record<MetricKey, any>>({
    mentions: null,
    shareOfVoice: null,
    coverage: null,
    position: null,
    ranking: null,
});

const metricsConfig: MetricConfig[] = [
    {
        key: "mentions",
        title: "Brand Mentions",
        icon: "i-heroicons-chat-bubble-left-right",
        endpoint: "/api/report/metrics/mentions",
    },
    {
        key: "shareOfVoice",
        title: "Share of Voice",
        icon: "i-heroicons-megaphone",
        endpoint: "/api/report/metrics/share-of-voice",
    },
    {
        key: "coverage",
        title: "Coverage",
        icon: "i-heroicons-globe-alt",
        endpoint: "/api/report/metrics/coverage",
    },
    {
        key: "position",
        title: "Position",
        icon: "i-heroicons-map-pin",
        endpoint: "/api/report/metrics/position",
    },
    {
        key: "ranking",
        title: "Ranking",
        icon: "i-heroicons-trophy",
        fullWidth: true,
        endpoint: "/api/report/metrics/ranking",
    },
];

const getQueryParams = () => ({
    brand: form.brand,
    brand_report_id: brandReportId,
    model: form.model,
    start_date: form.start_date || undefined,
    end_date: form.end_date || undefined,
});

const refreshAllMetrics = async () => {
    if (!form.brand) {
        toast.add({
            title: "Missing Field",
            description: "Brand name is required.",
            color: "secondary",
        });
        return;
    }

    loading.value = true;
    metricsConfig.forEach((metric) => {
        results[metric.key] = null;
    });

    try {
        const outcomes = await Promise.all(
            metricsConfig.map((metric) =>
                $fetch(metric.endpoint, { query: getQueryParams() })
                    .then((data) => ({
                        status: "fulfilled" as const,
                        key: metric.key,
                        data,
                    }))
                    .catch((error) => ({
                        status: "rejected" as const,
                        key: metric.key,
                        error,
                    })),
            ),
        );

        let errorCount = 0;
        outcomes.forEach((outcome) => {
            if (outcome.status === "fulfilled") {
                results[outcome.key] = outcome.data;
            } else {
                console.error(`Error fetching ${outcome.key}:`, outcome.error);
                errorCount += 1;
            }
        });

        if (errorCount > 0) {
            toast.add({
                title: "Partial Content",
                description: `${errorCount} metrics failed to load.`,
                color: "warning",
            });
        } else {
            toast.add({
                title: "Success",
                description: "All metrics updated.",
                color: "success",
            });
        }
    } catch (error) {
        console.error("Global error:", error);
        toast.add({
            title: "Error",
            description: "Failed to initiate requests.",
            color: "error",
        });
    } finally {
        loading.value = false;
    }
};

const formatLabel = (label: string) => label.replace(/_/g, " ");

const normalizeData = (data: any): { label: string; value: string }[] => {
    if (!data) return [];
    const payload = data?.data ?? data;
    if (!payload || typeof payload !== "object" || Array.isArray(payload))
        return [];

    return Object.entries(payload).map(([key, value]) => ({
        label: formatLabel(key),
        value:
            typeof value === "number"
                ? value.toLocaleString()
                : String(value ?? "—"),
    }));
};

const getRankingEntries = (data: any): RankingEntry[] => {
    if (!data) return [];
    const payload = data?.data ?? data;
    const list = Array.isArray(payload) ? payload : payload?.ranking;
    if (!Array.isArray(list)) return [];

    return list.map((row) => ({
        rank: typeof row?.rank === "number" ? row.rank : undefined,
        brand_name:
            typeof row?.brand_name === "string" ? row.brand_name : undefined,
        mention_count:
            typeof row?.mention_count === "number"
                ? row.mention_count
                : undefined,
    }));
};
</script>
