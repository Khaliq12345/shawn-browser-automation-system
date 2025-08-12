<script setup lang="ts">
const props = defineProps({
  menus: {
    type: Object,
    required: true
  },
  activeMenu: {
    type: Object,
    default: () => ({})
  },
})
const emit = defineEmits(['menu-item-clicked', 'close-sidebar'])
</script>

<template>
  <div class="flex flex-col p-4 bg-gray-100 text-black w-full h-full">
    <!-- Title -->
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-xl font-bold text-center w-full">Dashboard</h3>
      <div class="md:hidden">
        <UButton icon="i-heroicons-x-mark" variant="ghost" @click="$emit('close-sidebar')" />
      </div>
    </div>
    <div class="mb-2 w-full text-center">
      <h3 class="text-xl font-semibold">Menus List</h3>
    </div>
    <!-- Separator -->
    <USeparator class="my-4" color="neutral" size="md" />
    <!-- Listing the menus-->
    <nav class="flex-1 space-y-4 w-full">
      <UButton v-for="menu in props.menus" variant="ghost"
        class="text-black hover:bg-gray-700 hover:text-white flex items-center py-2 px-3 rounded-lg w-full"
        :class="{ 'bg-gray-800 text-white': menu['name'] === activeMenu['name'] }"
        @click="$emit('menu-item-clicked', menu)">
        <UIcon :name="menu.icon" class="mr-2 w-5 h-5" />
        <span class="flex-1 text-left">{{ menu['name'] }}</span>
      </UButton>
    </nav>
  </div>
</template>
