<script setup lang="ts">
const loadingData = ref(false);
const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
});
// Save User Interaction When Click on ~ Done ~
const saveInteraction = async () => {
  loadingData.value = true;
  try {
    var response = await $fetch("/api/save-interaction", {
      params: {
        user_id: props.user.scraped_user.user_id,
        creator_ig_username: props.user.ig_username,
        creator_username: props.user.creator_name,
      },
      headers: {
        'access_token': localStorage.getItem('access_token'),
        'refresh_token': localStorage.getItem('refresh_token')
      } as any
    });
  } catch (err) {
    console.error('Errors:', err);
  } finally {
    loadingData.value = false;
  }
};
</script>

<template>
  <div class="my-4 text-start">
    <div :key="user.scraped_user.id" class="flex bg-gray-100 rounded shadow">
      <div class="w-1 rounded-l bg-success-800"></div>
      <div class="pl-4 flex-1">
        <!-- User Infos -->
        <div class="flex justify-between">
          <h3 class="text-lg font-semibold">{{ user.scraped_user.username }} </h3>
          <a :href="user.scraped_user.profile_link" target="_blank">
            <UButton label="Visit to Interact" target="_blank"
              class="px-3 bg-warning-300 disabled:bg-warning-100 hover:bg-warning-200" icon="i-heroicons-eye" />
          </a>
        </div>
        <!-- More Details -->
        <p class="text-sm text-gray-500">Created At : {{ user.scraped_user.created_at }}</p>
        <div class="flex justify-between ">
          <p class="text-sm text-gray-500">Last Action : {{ user.scraped_user.last_action ?? " - - - " }}</p>
          <p class="text-sm text-gray-500">Related Account : <span class="font-bold">
              <UBadge class="bg-primary-100 rounded-full align-top">
                {{ user.ig_username }}</UBadge>
            </span> </p>
        </div>
        <!-- Done Button -->
        <div class="my-4  text-center">
          <UButton :loading="loadingData" @click="saveInteraction"
            class="px-12 w-1/2 justify-center bg-primary-300 disabled:bg-primary-100 hover:bg-primary-200"
            icon="i-heroicons-shield-check"> ~ Done ~ </UButton>
        </div>
      </div>
    </div>
  </div>
</template>
