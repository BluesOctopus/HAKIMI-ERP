import { defineStore } from 'pinia'
import { ref } from 'vue'

import {
  sendChatMessage,
  type ChatStep,
  type NavigationTarget,
  type PendingAction,
} from '@/api/modules/assistant'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  navigation?: NavigationTarget | null
  suggestions?: string[]
  steps?: ChatStep[]
  pendingAction?: PendingAction | null
  isError?: boolean
}

const WELCOME: ChatMessage = {
  role: 'assistant',
  content:
    "Hi! I'm the HAKIMI order-to-cash assistant. Give me a sales order number and I'll plan the run from picking all the way to settlement — nothing is executed until you confirm.",
  suggestions: [
    '把 SO00107 从拣配一路跑到平帐',
    '先给 SO00108 拣 50 件',
    '随便挑一笔开放订单跑全流程',
  ],
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export const useAssistantStore = defineStore('assistant', () => {
  const isOpen = ref(false)
  const loading = ref(false)
  const messages = ref<ChatMessage[]>([{ ...WELCOME }])

  function open() {
    isOpen.value = true
  }

  function close() {
    isOpen.value = false
  }

  function toggle() {
    isOpen.value = !isOpen.value
  }

  function reset() {
    messages.value = [{ ...WELCOME }]
  }

  /** Hide every outstanding confirm/cancel bar (plan answered or superseded). */
  function clearPendingActions() {
    for (const m of messages.value) {
      if (m.pendingAction) m.pendingAction = null
    }
  }

  async function ask(question: string, currentPath?: string, pendingAction?: PendingAction | null) {
    const text = question.trim()
    if (!text || loading.value) return

    clearPendingActions()
    messages.value.push({ role: 'user', content: text })
    loading.value = true
    try {
      const history = messages.value
        .filter((m) => !m.isError && m !== messages.value[0])
        .slice(0, -1) // exclude the question just pushed; it goes in `message`
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content }))

      const reply = await sendChatMessage({
        message: text,
        history,
        currentPath,
        pendingAction: pendingAction ?? undefined,
      })

      if (reply.steps && reply.steps.length > 0) {
        // Scripted demo flow: reveal the execution steps one by one so the
        // assistant looks like an agent working through tool calls.
        messages.value.push({
          role: 'assistant',
          content: '',
          navigation: null,
          suggestions: [],
          steps: [],
          pendingAction: null,
        })
        const live = messages.value[messages.value.length - 1]
        for (const step of reply.steps) {
          await sleep(650)
          live.steps!.push(step)
        }
        await sleep(350)
        live.content = reply.reply
        live.navigation = reply.navigation
        live.suggestions = reply.suggestions
        live.pendingAction = reply.pendingAction ?? null
      } else {
        messages.value.push({
          role: 'assistant',
          content: reply.reply,
          navigation: reply.navigation,
          suggestions: reply.suggestions,
          pendingAction: reply.pendingAction ?? null,
        })
      }
    } catch (err: any) {
      messages.value.push({
        role: 'assistant',
        content: err?.message || 'The assistant is unavailable right now. Please try again later.',
        isError: true,
      })
    } finally {
      loading.value = false
    }
  }

  /** User clicked "confirm" on a planned action: execute it server-side. */
  async function confirmPending(msg: ChatMessage, currentPath?: string) {
    const action = msg.pendingAction
    if (!action || loading.value) return
    await ask('确认执行', currentPath, action)
  }

  /** User clicked "cancel": dismiss locally, nothing was ever sent. */
  function cancelPending() {
    clearPendingActions()
    messages.value.push({ role: 'user', content: '取消' })
    messages.value.push({
      role: 'assistant',
      content: '好的，已取消该操作，未修改任何业务数据。',
      suggestions: ['随便挑一笔开放订单跑全流程'],
    })
  }

  return { isOpen, loading, messages, open, close, toggle, reset, ask, confirmPending, cancelPending }
})
