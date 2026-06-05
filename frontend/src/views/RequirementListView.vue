<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

onMounted(() => {
  router.replace({
    name: 'project-detail',
    params: { id: route.params.id },
    query: { tab: 'requirements' },
  })
})
</script>

<template>
  <div class="page-container" v-loading="true" />
</template>
