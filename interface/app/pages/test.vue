<script lang="ts" setup>
const categories: Record<string, BulletLegendItemInterface> = {
    nike: { name: "Nike" },
    walmart: { name: "Walmart" },
};

interface AreaChartItem {
    date: string;
    nike: number;
    walmart: number;
}

const AreaChartData: AreaChartItem[] = [
    { date: "2025-11-19T12:45:06", nike: 1, walmart: 3 },
    { date: "2025-11-20T12:45:06", nike: 3, walmart: 2 },
    { date: "2025-11-21T12:45:06", nike: 2, walmart: 1 },
];

const xFormatter = (tick: number, _i?: number, _ticks?: number[]): string => {
    return `${AreaChartData[tick]?.date ?? ""}`;
};
</script>

<template>
    <AreaChart
        :data="AreaChartData"
        :height="260"
        y-label="Revenue"
        x-label="Month"
        :categories="categories"
        :y-num-ticks="4"
        :x-num-ticks="7"
        :y-grid-line="true"
        :legend-position="LegendPosition.TopRight"
        :hide-legend="false"
        :x-formatter="xFormatter"
    />
</template>
