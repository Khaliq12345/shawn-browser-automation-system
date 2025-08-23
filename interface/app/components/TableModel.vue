<template>
  <div class="w-full">
    <UTable ref="table" :data="data" :columns="columns" sticky class="h-96">
      <template #expanded="{ row }">
        <pre>{{ row.original }}</pre>
      </template>
    </UTable>
    <div class="text-end mt-3 text-semibold text-sm lg:text-lg">
      Total of
      {{ table?.tableApi?.getFilteredRowModel().rows.length || 0 }} row(s)
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  data0: {
    type: Object,
    required: true,
  },
  columns0: {
    type: Object,
    required: true,
  },
});
const columns: any = props.columns0 ? props.columns0 : [];
const data: any = props.data0 ? props.data0 : [];
const table = useTemplateRef("table");
</script>
