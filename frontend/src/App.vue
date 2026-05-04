<template>
  <AppLayout>
    <RouterView v-slot="{ Component, route }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" :key="route.path" />
      </Transition>
    </RouterView>
  </AppLayout>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import AppLayout from '@/components/layout/AppLayout.vue'

const auth = useAuthStore()
const chat = useChatStore()

onMounted(async () => {
  await auth.init()
  // Підключаємо WebSocket якщо користувач авторизований
  if (auth.isLoggedIn) {
    chat.connectWS()
  }
})

onUnmounted(() => {
  chat.disconnectWS()
})
</script>
