<template>
  <div></div>
</template>

<script setup>
// Redirect to /home on launch
const router = useRouter();
onMounted(async () => {
  router.push("/home");
});
</script>

