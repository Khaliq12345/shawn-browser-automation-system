<template>
    <UCollapsible class="flex flex-col gap-3">
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
            <div class="p-4 space-y-4">
                <!-- Loading -->
                <div v-if="loading" class="text-primary">
                    Loading sentiments…
                </div>

                <!-- JSON Output -->
                <pre
                    v-else
                    class="text-sm bg-gray-100 p-4 text-primary rounded overflow-auto max-h-96"
                    >{{ JSON.stringify(sentiments, null, 2) }}
                </pre>
            </div>
        </template>
    </UCollapsible>
</template>

<script setup lang="ts">
const props = defineProps<{
    brandReportId: string;
    promptId: string;
    model: string;
    date?: string;
}>();

const loading = ref(false);
const sentiments = ref<any>(null);

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

        sentiments.value = res || {};
    } catch (e) {
        console.error("❌ Error loading sentiments:", e);
        sentiments.value = {};
    } finally {
        loading.value = false;
    }
}

onMounted(async () => {
    await loadSentiments();
});
</script>
