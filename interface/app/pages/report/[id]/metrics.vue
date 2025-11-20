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
                        :items="modelOptions"
                        clearable
                        placeholder="Select a model"
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

        <div v-if="loading" class="flex flex-col items-center gap-2">
            <UProgress animation="swing" color="secondary" class="w-full" />
            <span class="text-sm text-gray-500">Loading metrics...</span>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <UCard
                v-for="metric in metricsConfig"
                :key="metric.key"
                :class="['flex flex-col h-full', 'md:col-span-2']"
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
                                    class="flex flex-wrap items-center gap-2 rounded border border-gray-200 dark:border-gray-800 p-3 text-base hover:bg-gray-50 dark:hover:bg-gray-800 transition"
                                >
                                    <UBadge
                                        color="success"
                                        variant="soft"
                                        size="sm"
                                        >#{{ row.rank ?? "—" }}</UBadge
                                    >
                                    <span class="flex-1 font-medium truncate">{{
                                        row.brand_name ?? "Unknown"
                                    }}</span>
                                    <span class="text-sm text-gray-500"
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

        <UCard class="flex flex-col h-full md:col-span-2">
            <template #header>
                <div
                    class="flex items-center gap-2 font-semibold text-gray-800 dark:text-gray-100"
                >
                    <UIcon name="i-heroicons-chart-bar" class="w-5 h-5" />
                    <span>Ranking Over Time</span>
                </div>
            </template>

            <ClientOnly>
                <MetricsRankOverTime
                    :loading="rankingLoading"
                    :error="rankingError"
                    :rank-data="rankData"
                    :mention-data="mentionData"
                    :rank-categories="rankCategories"
                    :mention-categories="mentionCategories"
                    :format-rank-x-label="formatRankXLabel"
                    :format-mention-x-label="formatMentionXLabel"
                />
            </ClientOnly>
        </UCard>
    </UContainer>
</template>

<script setup lang="ts">
import MetricsRankOverTime from "~/components/metrics/RankOverTime.vue";
import { useRankingOverTime } from "~/composables/useRankingOverTime";
import { getMentionsMetrics } from "~/utils/getMentionsMetrics";
import { getShareOfVoiceMetrics } from "~/utils/getShareOfVoiceMetrics";
import { getCoverageMetrics } from "~/utils/getCoverageMetrics";
import { getPositionMetrics } from "~/utils/getPositionMetrics";
import { getRankingMetrics } from "~/utils/getRankingMetrics";

import { useToast } from "#imports"; // notifié par Zed (erreur sur const toast = useToast();)

import type {
    MetricConfig,
    MetricKey,
    MetricRequestParams,
    RankingEntry,
} from "~/types/metrics";

const route = useRoute();
const toast = useToast();
const brandReportId = String(route.params.id);
const loading = ref(false);
const refreshed = ref(false);
const refreshKey = ref(0);
const initialBrand =
    typeof route.query.brand === "string" ? route.query.brand : "";

const modelOptions = [
    { label: "All Models", value: "all" },
    { label: "ChatGPT", value: "chatgpt" },
    { label: "Perplexity", value: "perplexity" },
    { label: "Google", value: "google" },
];

const form = reactive({
    brand: initialBrand,
    model: "all",
    start_date: undefined as string | undefined,
    end_date: undefined as string | undefined,
});

const {
    loading: rankingLoading,
    error: rankingError,
    rankData,
    mentionData,
    rankCategories,
    mentionCategories,
    fetchRankingOverTime,
    formatRankXLabel,
    formatMentionXLabel,
} = useRankingOverTime();

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
    },
    {
        key: "shareOfVoice",
        title: "Share of Voice",
        icon: "i-heroicons-megaphone",
    },
    {
        key: "coverage",
        title: "Coverage",
        icon: "i-heroicons-globe-alt",
    },
    {
        key: "position",
        title: "Position",
        icon: "i-heroicons-map-pin",
    },
    {
        key: "ranking",
        title: "Ranking",
        icon: "i-heroicons-trophy",
    },
];

const metricFetchers: Record<
    MetricKey,
    (params: MetricRequestParams) => Promise<any>
> = {
    mentions: getMentionsMetrics,
    shareOfVoice: getShareOfVoiceMetrics,
    coverage: getCoverageMetrics,
    position: getPositionMetrics,
    ranking: getRankingMetrics,
};

const buildMetricParams = (): MetricRequestParams => ({
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
    refreshed.value = false;
    refreshKey.value += 1;
    metricsConfig.forEach((metric) => {
        results[metric.key] = null;
    });

    try {
        const params = buildMetricParams();
        const outcomes = await Promise.all(
            metricsConfig.map((metric) => {
                const fetcher = metricFetchers[metric.key];
                if (!fetcher) {
                    return Promise.resolve({
                        status: "rejected" as const,
                        key: metric.key,
                        error: new Error(
                            `No fetcher configured for ${metric.key}`,
                        ),
                    });
                }

                return fetcher(params)
                    .then((data) => ({
                        status: "fulfilled" as const,
                        key: metric.key,
                        data,
                    }))
                    .catch((error) => ({
                        status: "rejected" as const,
                        key: metric.key,
                        error,
                    }));
            }),
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
        refreshed.value = true;

        // Fetch ranking over time data
        await fetchRankingOverTime({
            brand: params.brand,
            brand_report_id: params.brand_report_id,
            model: params.model,
            start_date: params.start_date,
            end_date: params.end_date,
        });
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
    const payload = data?.data;
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
    const payload = data?.data;
    if (!payload) return [];
    const list: any[] = Array.isArray(payload?.ranking)
        ? (payload.ranking as any[])
        : [];

    return list.map((row: any) => ({
        rank: typeof row?.rank === "number" ? row.rank : undefined,
        brand_name:
            typeof row?.brand_name === "string" ? row.brand_name : undefined,
        mention_count:
            typeof row?.mention_count === "number"
                ? row.mention_count
                : undefined,
    }));
};

onMounted(() => {
    // Si le brand est rempli on déclenche le rafraîchissement
    if (form.brand) {
        refreshAllMetrics();
    }
});
</script>
