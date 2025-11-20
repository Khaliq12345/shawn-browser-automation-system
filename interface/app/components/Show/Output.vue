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
            Output
        </UButton>

        <template #content>
            <div class="p-4 space-y-4">
                <!-- Loading -->
                <div v-if="loading" class="text-gray-500">Loading output…</div>

                <!-- Snapshot -->
                <div v-if="output?.snapshot_url">
                    <h3 class="text-lg font-semibold">Snapshot</h3>
                    <img
                        :src="output.snapshot_url"
                        alt="Snapshot"
                        class="rounded-lg shadow-md"
                    />
                </div>

                <!-- Markdown -->
                <div v-if="output?.markdown">
                    <h3 class="text-lg font-semibold">Markdown File</h3>
                    <a
                        :href="output.markdown"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="text-blue-600 underline"
                    >
                        Open Markdown File
                    </a>
                </div>
            </div>
        </template>
    </UCollapsible>
</template>

<script setup lang="ts">
type OutputResponse = {
    snapshot_url: string;
    markdown: string;
};

const props = defineProps<{
    brandReportId: string;
    promptId: string;
    model: string;
    date?: string;
}>();

const loading = ref(false);
const output = ref<OutputResponse | null>(null);

async function fetchOutput() {
    loading.value = true;

    try {
        const res = await $fetch<OutputResponse>(
            "/api/report/prompts/outputs",
            {
                query: {
                    brand_report_id: props.brandReportId,
                    prompt_id: props.promptId,
                    model: props.model,
                    date: props.date,
                },
            },
        );

        output.value = res;
    } catch (e) {
        console.error("❌ fetchOutput error:", e);
        output.value = null;
    } finally {
        loading.value = false;
    }
}

onMounted(async () => {
    await fetchOutput();
});
</script>
