import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export type NotificationTone = 'info' | 'success' | 'warning' | 'danger'

export interface SystemNotification {
  id: number
  title: string
  text: string
  time: string
  tone: NotificationTone
  read: boolean
}

function formatRelativeTime(date: Date): string {
  const seconds = Math.max(1, Math.floor((Date.now() - date.getTime()) / 1000))
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  return date.toLocaleString()
}

let nextId = 1

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<SystemNotification[]>([])

  const unreadCount = computed(() => notifications.value.filter((item) => !item.read).length)

  function push(input: Omit<SystemNotification, 'id' | 'read' | 'time'> & { time?: string }) {
    notifications.value.unshift({
      id: Date.now() + nextId,
      read: false,
      time: input.time || formatRelativeTime(new Date()),
      title: input.title,
      text: input.text,
      tone: input.tone,
    })
    nextId += 1
    if (notifications.value.length > 50) notifications.value.length = 50
  }

  function markAllRead() {
    notifications.value.forEach((item) => {
      item.read = true
    })
  }

  function clear() {
    notifications.value = []
  }

  return { notifications, unreadCount, push, markAllRead, clear }
})
