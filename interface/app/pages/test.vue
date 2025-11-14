<script setup lang="ts">
import { ref } from "vue";

const brand_report_id = ref("");
const date = ref("");
const model = ref("all");

const loading = ref(false);
const result = ref<string | null>(null);
const error = ref<string | null>(null);

async function testSentiments() {
    loading.value = true;
    error.value = null;
    result.value = null;

    try {
        const params: Record<string, string> = {
            brand_report_id: brand_report_id.value,
            model: model.value || "all",
        };
        if (date.value) params.date = date.value;

        const res = await $fetch("/api/report/prompts/sentiments", {
            method: "GET",
            query: params,
        });

        result.value =
            typeof res === "string" ? res : JSON.stringify(res, null, 2);
    } catch (e: any) {
        error.value = e.message || "Erreur inconnue";
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <div class="max-w-xl mx-auto p-6">
        <h1 class="text-2xl font-bold mb-4">Test Sentiments Metrics</h1>

        <div class="mb-4">
            <label class="block font-semibold mb-1">Brand Report ID *</label>
            <input
                v-model="brand_report_id"
                type="text"
                class="border p-2 w-full"
                placeholder="brand_report_id"
            />
        </div>

        <div class="mb-4">
            <label class="block font-semibold mb-1">Date</label>
            <input v-model="date" type="date" class="border p-2 w-full" />
        </div>

        <div class="mb-4">
            <label class="block font-semibold mb-1">Model</label>
            <input
                v-model="model"
                type="text"
                class="border p-2 w-full"
                placeholder="model (default: all)"
            />
        </div>

        <button
            class="bg-blue-600 text-white px-4 py-2 rounded"
            :disabled="loading || !brand_report_id"
            @click="testSentiments"
        >
            {{ loading ? "Loading..." : "Run Sentiments Metrics" }}
        </button>

        <pre
            v-if="result"
            class="mt-4 bg-primary p-4 rounded overflow-auto max-h-96 whitespace-pre-wrap"
            >{{ result }}
    </pre
        >

        <p v-if="error" class="mt-4 text-red-600 font-semibold">
            {{ error }}
        </p>
    </div>
</template>
