<template>
    <UContainer class="py-8 space-y-6">
        <h1 class="text-2xl font-bold">Report Show Page</h1>

        <ShowOutput
            :brandReportId="brandReportId"
            :promptId="promptId"
            :model="model"
            :date="date"
        />
        <ShowCitation
            :brandReportId="brandReportId"
            :promptId="promptId"
            :model="model"
            :date="date"
        />
        <ShowSentiments
            :brandReportId="brandReportId"
            :promptId="promptId"
            :model="model"
            :date="date"
        />
    </UContainer>
</template>

<script setup lang="ts">
const route = useRoute();

const brandReportId = (route.query.brand_report_id as string) || "";
const promptId = (route.query.prompt_id as string) || "";
const model = (route.query.model as string) || "";
const date = (route.query.date as string) || "";
</script>
