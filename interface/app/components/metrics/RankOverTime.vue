<template>
    <div class="space-y-8">
        <div v-if="loading" class="flex flex-col items-center gap-2">
            <UProgress animation="swing" color="secondary" class="w-full" />
            <span class="text-sm text-gray-500">Chargement des tendances...</span>
        </div>

        <div v-else>
            <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
            <p v-else-if="!rankData.length && !positionData.length" class="text-sm text-gray-400">
                Aucune donnée disponible pour cette configuration.
            </p>
            <div v-else class="space-y-10">
                <div class="space-y-4">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-semibold">Classement dans le temps</h3>
                        <span class="text-xs text-gray-500">Basé sur les rangs cumulés</span>
                    </div>
                    <AreaChart
                        v-if="rankData.length"
                        :data="rankData"
                        index="date"
                        :categories="rankCategories"
                        :x-formatter="formatDateLabel"
                        :y-grid-line="true"
                    />
                </div>

                <div class="space-y-4">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-semibold">Position exacte</h3>
                        <span class="text-xs text-gray-500">Visualisation des positions calculées</span>
                    </div>
                    <AreaChart
                        v-if="positionData.length"
                        :data="positionData"
                        index="date"
                        :categories="positionCategories"
                        :x-formatter="formatDateLabel"
                        :y-grid-line="true"
                    />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">

type AxisFormatter = (tick: number, index?: number, ticks?: number[]) => string;

interface RankingPoint {
    date?: string;
    rank?: number;
    position?: number;
}

interface RankingEntryResponse {
    brand_name?: string;
    points?: RankingPoint[];
}

interface RankingOverTimeResponse {
    data?: {
        ranking?: RankingEntryResponse[];
    };
}

type AreaCategories = Record<string, { name: string; color: string }>;
type ChartRow = Record<string, string | number> & { date: number };

const colorPalette = ['#2563eb', '#dc2626', '#f97316', '#16a34a', '#9333ea', '#0ea5e9', '#facc15', '#14b8a6'];

const props = defineProps<{
    brand: string;
    brandReportId: string;
    model?: string;
    startDate?: string;
    endDate?: string;
}>();

const loading = ref(false);
const error = ref<string | null>(null);

const rankCategories = ref<AreaCategories>({});
const positionCategories = ref<AreaCategories>({});
const rankData = ref<ChartRow[]>([]);
const positionData = ref<ChartRow[]>([]);

const hasFilters = computed(() => Boolean(props.brand && props.brandReportId));

const parseTimestamp = (value?: string) => (value ? new Date(value).getTime() : null);

const formatDateLabel: AxisFormatter = (tick) => {
    if (!tick) return '';
    return new Intl.DateTimeFormat('fr-FR', {
        dateStyle: 'medium',
        timeStyle: 'short',
    }).format(new Date(tick));
};

const buildSeries = (ranking: RankingEntryResponse[] = [], valueKey: 'rank' | 'position') => {
    const brandOrder: string[] = [];
    const rows = new Map<number, ChartRow>();

    ranking.forEach((entry) => {
        const brandName = entry.brand_name?.trim() || 'Inconnu';
        if (!brandOrder.includes(brandName)) {
            brandOrder.push(brandName);
        }

        entry.points?.forEach((point) => {
            const timestamp = parseTimestamp(point.date);
            if (timestamp === null) return;

            if (!rows.has(timestamp)) {
                rows.set(timestamp, { date: timestamp });
            }

            const row = rows.get(timestamp)!;
            const baseValue = valueKey === 'rank' ? point.rank : point.position;
            row[brandName] = typeof baseValue === 'number' ? baseValue : point.rank ?? 0;
        });
    });

    const categories = brandOrder.reduce<AreaCategories>((acc, brand, index) => {
        const paletteColor = colorPalette[index % colorPalette.length] ?? '#64748b';
        acc[brand] = { name: brand, color: paletteColor };
        return acc;
    }, {});

    const series = [...rows.entries()]
        .sort((a, b) => a[0] - b[0])
        .map(([, payload]) => payload);

    return { categories, series };
};

const fetchRankingOverTime = async () => {
    if (!hasFilters.value) {
        rankData.value = [];
        positionData.value = [];
        rankCategories.value = {};
        positionCategories.value = {};
        return;
    }

    loading.value = true;
    error.value = null;

    try {
        const response = await $fetch<RankingOverTimeResponse>('/api/report/metrics/ranking-over-time', {
            query: {
                brand: props.brand,
                brand_report_id: props.brandReportId,
                model: props.model ?? 'all',
                start_date: props.startDate,
                end_date: props.endDate,
            },
        });

        const ranking = response?.data?.ranking ?? [];
        const rankSeries = buildSeries(ranking, 'rank');
        const positionSeries = buildSeries(ranking, 'position');

        rankCategories.value = rankSeries.categories;
        positionCategories.value = positionSeries.categories;
        rankData.value = rankSeries.series;
        positionData.value = positionSeries.series;
    } catch (fetchError) {
        console.error('Erreur Ranking Over Time:', fetchError);
        error.value = "Impossible de charger l'évolution du ranking.";
    } finally {
        loading.value = false;
    }
};

watch(
    () => [props.brand, props.brandReportId, props.model, props.startDate, props.endDate],
    () => {
        fetchRankingOverTime();
    },
    { immediate: true },
);
</script>
