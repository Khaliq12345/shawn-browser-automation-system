<template>
  <div class="min-h-screen flex">
    <!-- Sidebar -->
    <div class="hidden md:block md:w-4/12 lg:w-3/12">
      <DashboardSidebar :menus="menus" :active-menu="activeMenu" @menu-item-clicked="handleMenuItemClick" />
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
        <div class="flex justify-center">
          <div class="flex flex-col ml-4">
            <span class="mr-4 text-2xl mb-3">
              Welcome, <span class="font-bold"> Here </span> !
            </span>
          </div>
        </div>
        <div class="flex justify-end">
          
            Menu : <span class="font-semibold ml-1"> {{activeMenu.name}}
          </span>
        </div>
        <!-- Page Content -->
        <!-- Loading -->
        <div v-if="loadingData" class="place-items-center place-content-center my-15">
          <UProgress animation="swing" color="neutral" />
          <div class="container mx-auto p-4 text-center">
            <p>Loading Data ...</p>
          </div>
        </div>
        <!-- When Loaded -->
        <div v-else>
          <!-- Page content for active menu -->
          <DashboardContent :active-menu="activeMenu"/>
        </div>
      </main>
    </div>
    <!-- Mobile Drawer Sidebar -->
    <UDrawer direction="left" v-model:open="isMobileSidebarOpen" class="w-10/12 sm:w-6/12 bg-gray-100 ">
      <template #title>
      </template>
      <template #description>
      </template>
      <template #body>
        <DashboardSidebar :menus="menus" :active-menu="activeMenu" @menu-item-clicked="handleMenuItemClick" 
          @close-sidebar="isMobileSidebarOpen = false" />
      </template>
    </UDrawer>
  </div>
</template>

<script setup lang="ts">

import DashboardContent from '~/components/DashboardContent.vue';
import DashboardSidebar from '~/components/DashboardSidebar.vue';

// To Manage Page Loading
const loadingData = ref(false);

// To Show or Hide the Sidebar
const isMobileSidebarOpen = ref(false);

// When click on a menu from the sidebar
    const handleMenuItemClick = async (item: any) => {
        activeMenu.value = item;
    };

// List of Menus
const menus = ref([
  {
    'id' : 1,
    'name': 'Overall',
    'icon' : 'i-heroicons-lifebuoy'
  },
  {
    'id' : 2,
    'name': 'ChatGPT',
    'icon' : 'i-heroicons-bolt'
  },
  {
    'id' : 3,
    'name': 'Perplexity',
    'icon' : 'i-heroicons-bolt'
  },
  {
    'id' : 4,
    'name': 'Gemini',
    'icon' : 'i-heroicons-bolt'
  },
]);
const activeMenu: any = ref(menus.value[0]);

// On Mounted 
    onMounted(async () => {
        loadingData.value = true;
        try {
            // 
        } catch (err) {
            console.error('Errors:', err);
        } finally {
            loadingData.value = false;
        }
    });

</script>
