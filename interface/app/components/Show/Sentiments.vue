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
            <div class="p-4 space-y-4">
                <!-- Loading -->
                <div v-if="loading" class="text-center py-10">
                    <div class="mt-2 max-w-md mx-auto">
                        <UProgress indeterminate color="neutral" status />
                        <p class="text-gray-200 mt-1">Loading Sentiments...</p>
                    </div>
                </div>
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
const open = ref(true);

defineShortcuts({
    o: () => (open.value = !open.value),
});

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
