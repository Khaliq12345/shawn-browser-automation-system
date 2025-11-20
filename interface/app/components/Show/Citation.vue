<template>
    <UCollapsible class="flex flex-col gap-3">
        <UButton
            class="group"
            color="neutral"
            variant="subtle"
            block
            trailing-icon="i-lucide-chevron-down"
            :ui="{
                trailingIcon:
                    'group-data-[state=open]:rotate-180 transition-transform duration-200',
            }"
        >
            Citations
        </UButton>

        <template #content>
            <div class="p-4 space-y-4">
                <!-- Loading -->
                <div v-if="loading" class="text-gray-500">
                    Loading citations…
                </div>

                <!-- List -->
                <div v-else>
                    <UCard
                        v-for="(item, index) in list"
                        :key="item.id || index"
                        variant="subtle"
                        class="border border-gray-200 shadow-sm mb-6"
                    >
                        <template #header>
                            <h3 class="font-semibold text-lg">
                                {{ item.title || `Citation ${index + 1}` }}
                            </h3>
                        </template>

                        <!-- Body -->
                        <div class="space-y-1 text-left p-6 text-xl">
                            <p><strong>Brand:</strong> {{ item.brand }}</p>
                            <p><strong>Date:</strong> {{ item.date }}</p>
                            <p><strong>Domain:</strong> {{ item.domain }}</p>
                            <p>
                                <strong>URL: </strong>
                                <a
                                    :href="item.norm_url"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    class="text-blue-600 underline"
                                >
                                    {{ item.norm_url }}
                                </a>
                            </p>
                        </div>
                    </UCard>

                    <div
                        v-if="list.length === 0"
                        class="text-gray-500 text-center"
                    >
                        No citations found.
                    </div>
                </div>
            </div>
        </template>
    </UCollapsible>
</template>

<script setup lang="ts">
const props = defineProps<{
    brandReportId: string;
    model?: string;
    date?: string;
}>();

const loading = ref(false);
const list = ref<any[]>([]);

type Citation = {
    id?: string | number;
    title?: string;
    brand?: string;
    [key: string]: any;
};

type CitationsResponse = {
    citations: Citation[];
};

async function fetchCitations() {
    loading.value = true;

    try {
        const res = await $fetch<CitationsResponse>(
            "/api/report/prompts/citations",
            {
                query: {
                    brand_report_id: props.brandReportId,
                    model: props.model || "all",
                    date: props.date,
                },
            },
        );

        list.value = res.citations;
    } catch (e) {
        console.error("❌ fetchCitations error:", e);
        list.value = [];
    } finally {
        loading.value = false;
    }
}

onMounted(async () => {
    await fetchCitations();
});
</script>
