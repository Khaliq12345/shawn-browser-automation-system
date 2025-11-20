<template>
    <div class="space-y-8">
        <div v-if="props.loading" class="flex flex-col items-center gap-2">
            <UProgress animation="swing" color="secondary" class="w-full" />
            <span class="text-sm text-gray-500">Loading trends...</span>
        </div>

        <div v-else>
            <p v-if="props.error" class="text-sm text-red-500">
                {{ props.error }}
            </p>
            <p
                v-else-if="!props.rankData.length && !props.mentionData.length"
                class="text-sm text-gray-400"
            >
                No data available for this configuration.
            </p>
            <div v-else class="space-y-10">
                <div class="space-y-4">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-semibold">
                            <!--Ranking Over Time-->
                        </h3>
                        <span class="text-xs text-gray-500"
                            >Based on cumulative ranks</span
                        >
                    </div>
                    <div ref="rankContainer" class="w-full">
                        <BarChart
                            v-if="props.rankData.length"
                            :data="props.rankData"
                            x-axis="date"
                            :categories="props.rankCategories"
                            :x-formatter="props.formatRankXLabel"
                            :y-grid-line="true"
                            :y-axis="rankYAxisKeys"
                            :height="rankHeight"
                            :group-padding="8"
                            :bar-padding="0.1"
                            :radius="4"
                        />
                        <p v-else class="text-sm text-gray-400 italic">
                            No ranking data available for this configuration.
                        </p>
                    </div>
                </div>

                <div class="space-y-4">
                    <div class="flex items-center justify-between">
                        <h3 class="text-lg font-semibold">
                            Number of mentions
                        </h3>
                        <span class="text-xs text-gray-500"
                            >Mentions visualization</span
                        >
                    </div>
                    <div ref="mentionContainer" class="w-full">
                        <BarChart
                            v-if="props.mentionData.length"
                            :data="props.mentionData"
                            x-axis="date"
                            :categories="props.mentionCategories"
                            :x-formatter="props.formatMentionXLabel"
                            :y-grid-line="true"
                            :y-axis="mentionYAxisKeys"
                            :height="mentionHeight"
                            :group-padding="8"
                            :bar-padding="0.1"
                            :radius="4"
                        />
                        <p v-else class="text-sm text-gray-400 italic">
                            No mentions data available for this configuration.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { AreaCategories, ChartRow } from "../../types/ranking";

const props = defineProps<{
    loading: boolean;
    error: string | null;
    rankData: ChartRow[];
    mentionData: ChartRow[];
    rankCategories: AreaCategories;
    mentionCategories: AreaCategories;
    formatRankXLabel: (tick: any, i?: number) => string;
    formatMentionXLabel: (tick: any, i?: number) => string;
}>();

// Keys pour l'axe Y : extraites des catégories
const rankYAxisKeys = computed(() => Object.keys(props.rankCategories));
const mentionYAxisKeys = computed(() => Object.keys(props.mentionCategories));

// Observers pour rendre la taille responsive
const rankContainer = ref<HTMLElement | null>(null);
const mentionContainer = ref<HTMLElement | null>(null);
const rankHeight = ref(260);
const mentionHeight = ref(260);
let rankObserver: ResizeObserver | null = null;
let mentionObserver: ResizeObserver | null = null;

const computeHeightFromWidth = (width: number) =>
    Math.max(200, Math.min(520, Math.round(width * 0.28)));

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
    mentionObserver = createObserver(mentionContainer.value, mentionHeight);
});

onBeforeUnmount(() => {
    if (rankObserver) rankObserver.disconnect();
    if (mentionObserver) mentionObserver.disconnect();
});
</script>
