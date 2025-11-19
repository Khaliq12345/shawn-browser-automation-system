<template>
    <div class="max-w-6xl mx-auto py-10 space-y-10">
        <h1 class="text-3xl font-bold">Reports</h1>

        <!-- Loading -->
        <div v-if="loading" class="text-center py-10">
            <p>Loading...</p>
        </div>

        <!-- Cards -->
        <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <UCard
                v-for="report in reports"
                :key="report.brand_report_id"
                class="shadow-md"
            >
                <template #header>
                    <h2 class="text-xl font-semibold">{{ report.brand }}</h2>
                </template>

                <template #default>
                    <div class="text-left space-y-1">
                        <p><strong>ID:</strong> {{ report.brand_report_id }}</p>
                        <p>
                            <strong>Date:</strong>
                            {{ new Date(report.date).toLocaleString() }}
                        </p>
                        <p>
                            <strong>languague:</strong> {{ report.languague }}
                        </p>
                        <p><strong>Country:</strong> {{ report.country }}</p>
                        <p><strong>Domain:</strong> {{ report.domain }}</p>
                    </div>
                </template>

                <template #footer>
                    <div class="flex justify-between pt-2">
                        <UButton
                            color="neutral"
                            size="sm"
                            variant="outline"
                            @click="goTo(report.brand_report_id, 'outputs')"
                        >
                            Show Outputs
                        </UButton>

                        <UButton
                            color="neutral"
                            size="sm"
                            variant="outline"
                            @click="goTo(report.brand_report_id, 'metrics')"
                        >
                            Show Metrics
                        </UButton>
                    </div>
                </template>
            </UCard>
        </div>

        <!-- Empty list -->
        <div v-if="!loading && isEmpty" class="text-center py-10 text-gray-500">
            No reports found.
        </div>

        <!-- Pagination -->
        <div class="flex justify-center gap-4">
            <UButton
                color="neutral"
                variant="solid"
                :disabled="page === 1"
                @click="previousPage"
            >
                Previous
            </UButton>

            <UButton
                color="neutral"
                variant="solid"
                :disabled="isEmpty"
                @click="nextPage"
            >
                Next
            </UButton>
        </div>
    </div>
</template>

<script setup lang="ts">
const reports = ref<any[]>([]);
const loading = ref(false);
const isEmpty = ref(false);

const page = ref(1);
const limit = 20;

const router = useRouter();

async function loadReports() {
    loading.value = true;
    isEmpty.value = false;

    try {
        const { data, error } = await useFetch("/api/reports", {
            method: "GET",
            query: {
                page: page.value,
                limit,
            },
        });

        if (error.value) {
            console.error("❌ API Error:", error.value);
            reports.value = [];
            isEmpty.value = true;
            return;
        }

        reports.value = data.value || [];
        isEmpty.value = reports.value.length === 0;
    } catch (err) {
        console.error("Error fetching reports:", err);
    } finally {
        loading.value = false;
    }
}

function nextPage() {
    page.value++;
    loadReports();
}

function previousPage() {
    if (page.value > 1) {
        page.value--;
        loadReports();
    }
}

function goTo(id: string, type: string) {
    router.push(`/${id}/${type}`);
}

onMounted(async () => {
    await loadReports();
});
</script>
