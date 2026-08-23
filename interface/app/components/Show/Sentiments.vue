<template>
    <UCollapsible v-model:open="open" class="flex flex-col gap-3">
        <UButton
            class="group"
            color="neutral"
            variant="subtle"
            block
            label="Sentiments"
            trailing-icon="i-lucide-chevron-down"
            :ui="{
                trailingIcon:
                    'group-data-[state=open]:rotate-180 transition-transform duration-200',
            }"
        />

        <template #content>
            <div class="p-4 space-y-6">
                <div v-if="loading" class="text-center py-10">
                    <UProgress indeterminate color="neutral" status />
                    <p class="text-gray-200 mt-1">Loading Sentiments...</p>
                </div>

                <div
                    v-else-if="
                        categoryKeys.length > 0 && positiveData.length > 0
                    "
                >
                    <h3 class="text-lg font-semibold mb-2">
                        Positive Sentiments
                    </h3>
                    <BarChart
                        :data="positiveData"
                        :categories="categories"
                        :y-axis="categoryKeys"
                        :height="300"
                        :x-formatter="xFormatter"
                        :y-formatter="yFormatter"
                        :legend-position="'TopRight'"
                        :radius="4"
                        :x-num-ticks="6"
                        :y-grid-line="true"
                    />

                    <h3 class="text-lg font-semibold mt-8 mb-2">
                        Negative Sentiments
                    </h3>
                    <BarChart
                        :data="negativeData"
                        :categories="categories"
                        :y-axis="categoryKeys"
                        :height="300"
                        :x-formatter="xFormatter"
                        :y-formatter="yFormatter"
                        :legend-position="'TopRight'"
                        :radius="4"
                        :x-num-ticks="6"
                        :y-grid-line="true"
                    />

                    <div class="mt-5">SENTIMENTS RAW</div>
                    <vue-json-pretty :data="sentiments" />
                </div>

                <div v-else class="text-center text-gray-400">
                    Pas de données disponibles pour afficher les graphiques.
                </div>
            </div>
        </template>
    </UCollapsible>
</template>

<script setup lang="ts">
import VueJsonPretty from "vue-json-pretty";
import "vue-json-pretty/lib/styles.css";

const props = defineProps<{
    brandReportId: string;
    promptId: string;
    model: string;
    date?: string;
}>();

const loading = ref(false);
const sentiments = ref<any[]>([]);
const open = ref(true);

async function loadSentiments() {
    loading.value = true;
    try {
        const res = await $fetch("/api/report/prompts/sentiments", {
            query: {
                brand_report_id: props.brandReportId,
                prompt_id: props.promptId,
                model: props.model,
                date: props.date,
            },
        });
        sentiments.value = res.sentiments || [];
    } catch (e) {
        console.error("❌ Error loading sentiments:", e);
        sentiments.value = [];
    } finally {
        loading.value = false;
    }
}

// Construction des catégories: { nike: { name: 'Nike', color: '#...' }, ... }
const categories = computed(() => {
    const brands = Array.from(
        new Set(sentiments.value.map((item) => item.brand)),
    );
    const colors = [
        "#3b82f6", // bleu
        "#22c55e", // vert
        "#f97316", // orange
        "#6366f1", // violet
        "#e11d48", // rouge
    ];
    const cat: Record<string, { name: string; color: string }> = {};
    brands.forEach((brand, i) => {
        cat[brand] = { name: brand, color: colors[i % colors.length] };
    });
    return cat;
});

const categoryKeys = computed(() => Object.keys(categories.value));

// Transformation des données en format BarChart:
// On veut des tableaux [{ date: "2025-11-20", Nike: 2, Walmart: 3, ...}, ...]

// Pour gérer plusieurs dates, on va grouper par date.

function groupDataByDate(
    sentimentsArray: any[],
    countKey: "count_positive_phrases" | "count_negative_phrases",
) {
    const grouped: Record<string, Record<string, number>> = {}; // date => { brand: count }
    for (const item of sentimentsArray) {
        const dateKey = item.date.split(" ")[0]; // garder juste la date sans l'heure
        if (!grouped[dateKey]) grouped[dateKey] = {};
        grouped[dateKey][item.brand] = item[countKey] || 0;
    }

    // Construit le tableau final avec toutes les marques présentes dans categories
    const allBrands = categoryKeys.value;
    const result = Object.entries(grouped).map(([date, counts]) => {
        const obj: Record<string, any> = { date };
        for (const brand of allBrands) {
            obj[brand] = counts[brand] ?? 0;
        }
        return obj;
    });

    // Si pas de données, on peut retourner un tableau vide
    return result.length > 0 ? result : [];
}

const positiveData = computed(() =>
    groupDataByDate(sentiments.value, "count_positive_phrases"),
);
const negativeData = computed(() =>
    groupDataByDate(sentiments.value, "count_negative_phrases"),
);

// Formatters pour axes
const xFormatter = (i: number) => {
    const date = positiveData.value[i]?.date || "";
    return date;
};

const yFormatter = (tick: number) => tick.toString();

onMounted(async () => {
    await loadSentiments();
});
</script>
