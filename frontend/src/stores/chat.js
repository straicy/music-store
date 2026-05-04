import { defineStore } from 'pinia'
import { ref } from 'vue'
import { messagesApi } from '@/api'
import { tokenStorage } from '@/api/axios'
import { useToast } from 'vue-toastification'

export const useChatStore = defineStore('chat', () => {
  const toast = useToast()

  // ── State ──────────────────────────────────────────────
  const conversations    = ref([])
  const activeMessages   = ref([])
  const activeConvId     = ref(null)
  const unreadTotal      = ref(0)
  const loading          = ref(false)

  let ws = null
  let reconnectTimer = null

  // ── WebSocket ──────────────────────────────────────────

  function connectWS() {
    const token = tokenStorage.getAccess()
    if (!token || ws?.readyState === WebSocket.OPEN) return

    const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
    const url = `${protocol}://${location.host}/api/messages/ws?token=${token}`

    ws = new WebSocket(url)

    ws.onopen = () => {
      console.log('🔌 WebSocket підключено')
      // Пінгуємо кожні 30 сек щоб з'єднання не обривалось
      reconnectTimer = setInterval(() => {
        if (ws?.readyState === WebSocket.OPEN) ws.send('ping')
      }, 30_000)
    }

    ws.onmessage = (event) => {
      if (event.data === 'pong') return

      try {
        const payload = JSON.parse(event.data)
        handleWSMessage(payload)
      } catch { /* ігноруємо некоректні дані */ }
    }

    ws.onclose = () => {
      console.log('🔌 WebSocket закрито, перепідключення через 3с...')
      clearInterval(reconnectTimer)
      setTimeout(connectWS, 3000)
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  function disconnectWS() {
    clearInterval(reconnectTimer)
    ws?.close()
    ws = null
  }

  function handleWSMessage(payload) {
    if (payload.type === 'new_message') {
      const msg = payload.message

      // Якщо відкрита саме ця розмова — додаємо повідомлення
      if (activeConvId.value === msg.conversation_id) {
        activeMessages.value.push({
          id: msg.id,
          sender_id: msg.sender_id,
          sender_name: msg.sender_name,
          text: msg.text,
          is_read: false,
          created_at: new Date(msg.created_at),
        })
      } else {
        // Інакше оновлюємо лічильник непрочитаних
        const conv = conversations.value.find(
          (c) => c.conversation_id === msg.conversation_id
        )
        if (conv) {
          conv.last_message = msg.text
          conv.last_message_at = msg.created_at
          conv.unread_count++
        }
        unreadTotal.value++
        toast.info(`💬 ${msg.sender_name}: ${msg.text.slice(0, 40)}...`)
      }
    }
  }

  // ── REST Actions ───────────────────────────────────────

  async function fetchConversations() {
    loading.value = true
    try {
      const { data } = await messagesApi.getConversations()
      conversations.value = data.conversations
      unreadTotal.value = data.conversations.reduce(
        (sum, c) => sum + c.unread_count, 0
      )
    } catch {
      toast.error('Не вдалось завантажити розмови')
    } finally {
      loading.value = false
    }
  }

  async function openConversation(convId) {
    activeConvId.value = convId
    loading.value = true
    try {
      const { data } = await messagesApi.getConversation(convId)
      activeMessages.value = data.messages

      // Обнуляємо лічильник цієї розмови
      const conv = conversations.value.find((c) => c.conversation_id === convId)
      if (conv) {
        unreadTotal.value = Math.max(0, unreadTotal.value - conv.unread_count)
        conv.unread_count = 0
      }
    } catch {
      toast.error('Не вдалось завантажити повідомлення')
    } finally {
      loading.value = false
    }
  }

  async function sendMessage(receiverId, listingId, text) {
    try {
      const { data } = await messagesApi.send({
        receiver_id: receiverId,
        listing_id: listingId,
        text,
      })
      // Своє повідомлення одразу додаємо локально
      activeMessages.value.push({
        id: data.id,
        sender_id: 'me',
        text,
        is_read: false,
        created_at: new Date(),
      })
      return data
    } catch (err) {
      toast.error('Помилка надсилання')
      throw err
    }
  }

  return {
    conversations, activeMessages, activeConvId,
    unreadTotal, loading,
    connectWS, disconnectWS,
    fetchConversations, openConversation, sendMessage,
  }
})
