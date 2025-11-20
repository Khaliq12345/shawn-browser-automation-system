<template>
    <div class="space-y-8">
        <div v-if="loading" class="flex flex-col items-center gap-2">
            <UProgress animation="swing" color="secondary" class="w-full" />
            <span class="text-sm text-gray-500"
                >Chargement des tendances...</span
            >
        </div>

        <div v-else>
            <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
            <p
                v-else-if="!rankData.length && !positionData.length"
                class="text-sm text-gray-400"
            >
                Aucune donnée disponible pour cette configuration.
            </p>
            <div v-else class="space-y-10">
                <div class="space-y-4">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-semibold">
                            Classement dans le temps
                        </h3>
                        <span class="text-xs text-gray-500"
                            >Basé sur les rangs cumulés</span
                        >
                    </div>
                    <div ref="rankContainer" class="w-full">
                        <BarChart
                            v-if="rankData.length"
                            :data="rankData"
                            x-axis="date"
                            :categories="rankCategories"
                            :x-formatter="formatRankXLabel"
                            :y-grid-line="true"
                            :y-axis="rankYAxisKeys"
                            :height="rankHeight"
                            :group-padding="8"
                            :bar-padding="0.1"
                            :radius="4"
                        />
                        <p v-else class="text-sm text-gray-400 italic">
                            Aucune donnée de classement disponible pour cette
                            configuration.
                        </p>
                    </div>
                </div>

                <div class="space-y-4">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-semibold">Position exacte</h3>
                        <span class="text-xs text-gray-500"
                            >Visualisation des positions calculées</span
                        >
                    </div>
                    <div ref="positionContainer" class="w-full">
                        <BarChart
                            v-if="positionData.length"
                            :data="positionData"
                            x-axis="date"
                            :categories="positionCategories"
                            :x-formatter="formatPositionXLabel"
                            :y-grid-line="true"
                            :y-axis="positionYAxisKeys"
                            :height="positionHeight"
                            :group-padding="8"
                            :bar-padding="0.1"
                            :radius="4"
                        />
                        <p v-else class="text-sm text-gray-400 italic">
                            Aucune position disponible pour cette configuration.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRankingOverTime } from "../../composables/useRankingOverTime";

const props = defineProps<{
    brand: string;
    brandReportId: string;
    model?: string;
    startDate?: string;
    endDate?: string;
}>();

// Utilisation du composable
const {
    loading: loadingRef,
    error: errorRef,
    rankCategories,
    positionCategories,
    rankData,
    positionData,
    fetchRankingOverTime,
    formatRankXLabel,
    formatPositionXLabel,
} = useRankingOverTime();

// Liaison refs locales
const loading = loadingRef;
const error = errorRef;

// Keys pour l'axe Y : extraites des catégories
const rankYAxisKeys = computed(() => Object.keys(rankCategories.value));
const positionYAxisKeys = computed(() => Object.keys(positionCategories.value));

// Observers pour rendre la taille responsive
const rankContainer = ref<HTMLElement | null>(null);
const positionContainer = ref<HTMLElement | null>(null);
const rankHeight = ref(260);
const positionHeight = ref(260);
let rankObserver: ResizeObserver | null = null;
let positionObserver: ResizeObserver | null = null;

const computeHeightFromWidth = (width: number) =>
    Math.max(200, Math.min(520, Math.round(width * 0.28)));

// Watcher pour les props : déclenche le fetch à chaque changement
watch(
    () => [
        props.brand,
        props.brandReportId,
        props.model,
        props.startDate,
        props.endDate,
    ],
    () => {
        if (props.brand && props.brandReportId) {
            void fetchRankingOverTime({
                brand: props.brand,
                brand_report_id: props.brandReportId,
                model: props.model ?? "all",
                start_date: props.startDate ?? null,
                end_date: props.endDate ?? null,
            });
        }
    },
    { immediate: true },
);

onMounted(() => {
    if (typeof window === "undefined" || !("ResizeObserver" in window)) return;

    const createObserver = (
        container: HTMLElement | null,
        height: Ref<number>,
    ) => {
        if (container) {
            const observer = new ResizeObserver((entries) => {
                const rect = entries[0]?.contentRect;
                if (rect) height.value = computeHeightFromWidth(rect.width);
            });
            observer.observe(container);
            return observer;
        }
        return null;
    };

    rankObserver = createObserver(rankContainer.value, rankHeight);
    positionObserver = createObserver(positionContainer.value, positionHeight);
});

onBeforeUnmount(() => {
    if (rankObserver) rankObserver.disconnect();
    if (positionObserver) positionObserver.disconnect();
});
</script>
