<template>
  <div>
    <!-- Refresh Logs -->
    <div class="justify-end flex">
      <UButton
        label="Refresh Logs"
        :disabled="logGot.length == 0"
        icon="i-heroicons-arrow-path"
        :loading="loading"
        class="justify-center text-white my-4"
        @click="getLogs"
      />
    </div>
    <!-- Showing Logs -->
    <UTextarea
      :rows="20"
      :autoresize="false"
      v-model="logGot"
      :disabled="true"
      class="w-full textarea whitespace-pre font-mono"
      placeholder="Nothing to show ..."
    />
  </div>
</template>

<script setup lang="ts">
// Variables
const logGot = ref("-Nothing to Show !");
const loading = ref(false);
// Routing
const route = useRoute();
const currentPlatform: any = computed(() => route.name);
// Get Logs
const getLogs = async () => {
  logGot.value = "";
  loading.value = true;
  try {
    // Fetch Logs for {currentPlatform}'s last process '
    let lastrun = await getLastRunTimestamp(currentPlatform.value);
    if (!lastrun) {
      return;
    }
    const process_id = lastrun.process_id;
    const response = (await $fetch(`/api/logs/${process_id}`, {
      method: "GET",
    })) as any;
    logGot.value = response.details;
  } catch (error) {
    console.error("Erreur de requete:", error);
  } finally {
    loading.value = false;
  }
};
// On Startup
onMounted(async () => {
  getLogs();
});
</script>
