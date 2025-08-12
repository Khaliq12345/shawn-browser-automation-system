<template>
  <div>
    <!-- Showing -->
    <UTextarea :rows="20" :autoresize="false" v-model="logGot" :disabled="true"
      class="w-full mb-4 textarea whitespace-pre font-mono " placeholder="Nothing to show ..." />
    <!-- Refresh -->
    <div class="justify-start flex">
      <UButton label="Refresh Logs" :disabled="logGot.length == 0" icon="i-heroicons-arrow-path" :loading="loading"
        class="justify-center text-white" @click="getLogs" />
    </div>
  </div>
</template>

<script setup lang="ts">

// Variables
const logGot = ref("-djjdkkdll\n-djffof");
const loading = ref(false);
// 
const getLogs = async () => {
  loading.value = true
  try {
    // Fetch Logs

  } catch (error) {
    console.error('Erreur de requete:', error);
  } finally {
    loading.value = false
  }
}

</script>
