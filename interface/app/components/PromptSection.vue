<template>
  <div>
    <!-- Form -->
    <UForm
      :validate="validate"
      :state="state"
      class="space-y-4 w-full"
      @submit="onSubmit"
    >
      <UFormField label="Enter Your Prompt" name="prompt">
        <UInput v-model="state.prompt" class="w-full" />
      </UFormField>

      <UButton
        type="submit"
        label="Start Browser"
        :loading="loading"
        class="justify-center text-white my-2 px-5 text-lg"
      />
    </UForm>
  </div>
</template>

<script setup lang="ts">
import type { FormError, FormSubmitEvent } from "@nuxt/ui";
// Routing
const route = useRoute();
const currentPlatform: any = computed(() => route.name);
// Variables
const loading = ref(false);
const toast = useToast();
// Form
const state = reactive({
  prompt: "",
});
const validate = (state: any): FormError[] => {
  const errors = [];
  if (!state.prompt) errors.push({ name: "prompt", message: "Field Required" });
  return errors;
};
// Submit
async function onSubmit(event: FormSubmitEvent<typeof state>) {
  console.log("Event Data : ", event.data);
  try {
    loading.value = true;
    // Start The Browser'
    const response = await startBrowser(state.prompt, currentPlatform.value);
    // console.log("responde : ", response)
    toast.add({
      title: "Success",
      description: `${response.message} - ${response.process_id}`,
      color: "success",
    });
    state.prompt = "";
  } catch (error) {
    console.error("Erreur de requete:", error);
    toast.add({
      title: "Error",
      description: `Submitting Error - ${error}`,
      color: "error",
    });
  } finally {
    loading.value = false;
  }
}
</script>
