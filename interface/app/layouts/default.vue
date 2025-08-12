<template>
  <div class="min-h-screen flex">
    <!-- Sidebar -->
    <div class="hidden md:block md:w-4/12 lg:w-3/12">
      <Sidebar />
    </div>
    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden w-full ">
      <!-- Header -->
      <header class="bg-gray-200 shadow-sm py-4 px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between md:justify-end">
          <!-- Mobile Menu Button -->
          <UButton @click="isMobileSidebarOpen = true" :disabled="isMobileSidebarOpen"
            class="bg-gray-100 hover:bg-gray-300 md:hidden cursor-pointer">
            <UIcon name="i-heroicons-bars-3-bottom-left-20-solid" class="mr-3 text-xl" />
            <h3 class="ml-3 text-lg font-semibold text-center">Menu</h3>
          </UButton>
        </div>
        <!-- <USeparator /> -->
      </header>
      <!-- Main Content -->
      <main class="flex-1 text-center overflow-y-auto p-4 sm:p-6 lg:p-8">
        <NavBar />
        <!-- Page Content -->
        <slot />
      </main>
    </div>
    <!-- Mobile Drawer Sidebar -->
    <UDrawer direction="left" v-model:open="isMobileSidebarOpen" class="w-10/12 sm:w-6/12 bg-gray-100 ">
      <template #title>
      </template>
      <template #description>
      </template>
      <template #body>
        <Sidebar />
      </template>
    </UDrawer>
  </div>
</template>

<script setup lang="ts">
// To Show or Hide the Sidebar
const isMobileSidebarOpen = ref(false);
</script>
