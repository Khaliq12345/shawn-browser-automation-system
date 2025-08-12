<script setup lang="ts">

const props = defineProps({
  activeMenu: {
    type: Object,
    default: {}
  },
});
</script>

<template>
  <div class="mt-8">
    <!-- Overall-->
    <div v-if="activeMenu.id == 1">
      <OverallIndex/>
    </div>
    <!-- ChatGPT-->
    <div v-else-if="activeMenu.id == 2">
      <ChatGPTIndex/>
    </div>
    <!-- Perplexity-->
    <div v-else-if="activeMenu.id == 3">

    </div>
    <!-- Gemini-->
    <div v-else-if="activeMenu.id == 4">

    </div>
    <!-- Not Found-->
    <div v-else>
      <h2 class="text-lg mb-5">No Content Found !</h2>
    </div>

  </div>
</template>
