<template>
  <div class="chat-root">
    <!-- Floating launcher (draggable) -->
    <button
      v-if="!store.isOpen"
      class="chat-launcher"
      :style="{ left: launcherPos.x + 'px', top: launcherPos.y + 'px' }"
      title="Ask the assistant (drag to move)"
      @pointerdown="onLauncherPointerDown"
      @click="onLauncherClick"
    >
      <svg viewBox="0 0 24 24" width="24" height="24">
        <path
          d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v8a2.5 2.5 0 0 1-2.5 2.5H9l-4.2 3.4c-.4.3-.8 0-.8-.4V5.5z"
          fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"
        />
        <path d="M8.5 9h7M8.5 12h4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
      </svg>
    </button>

    <!-- Chat window (draggable by header) -->
    <transition name="chat-pop">
      <div
        v-if="store.isOpen"
        class="chat-window"
        :style="{ left: winPos.x + 'px', top: winPos.y + 'px' }"
      >
        <header class="chat-header" @pointerdown="onWinPointerDown">
          <div class="chat-header-icon">
            <svg viewBox="0 0 52 52" width="26" height="26">
              <circle cx="22" cy="18" r="9" fill="none" stroke="#FBFADA" stroke-width="2"/>
              <path d="M14 29c0-4.4 3.6-8 8-8s8 3.6 8 8" fill="none" stroke="#FBFADA" stroke-width="2" stroke-linecap="round"/>
              <circle cx="19" cy="17" r="1.4" fill="#FBFADA"/>
              <circle cx="25" cy="17" r="1.4" fill="#FBFADA"/>
              <path d="M18 23h8" fill="none" stroke="#FBFADA" stroke-width="1.6" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="chat-header-text">
            <span class="chat-title">HAKIMI Assistant</span>
            <span class="chat-subtitle">Navigation & workflow guide</span>
          </div>
          <button class="chat-header-btn" title="Clear conversation" @click="store.reset()">
            <svg viewBox="0 0 20 20" width="15" height="15">
              <path d="M4 10a6 6 0 1 1 1.8 4.3M4 10V5.5M4 10h4.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="chat-header-btn" title="Close" @click="store.close()">
            <svg viewBox="0 0 20 20" width="15" height="15">
              <path d="M5 5l10 10M15 5L5 15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </button>
        </header>

        <div ref="messagesEl" class="chat-messages">
          <div
            v-for="(msg, i) in store.messages"
            :key="i"
            class="msg-row"
            :class="msg.role"
          >
            <div class="msg-bubble" :class="{ 'msg-error': msg.isError }">
              <ul v-if="msg.steps?.length" class="msg-steps">
                <li v-for="(st, k) in msg.steps" :key="k" class="msg-step">
                  <span class="msg-step-icon">{{ st.icon }}</span>
                  <span class="msg-step-text">{{ st.text }}</span>
                </li>
              </ul>
              <p v-if="msg.content" class="msg-text">{{ msg.content }}</p>

              <div v-if="msg.pendingAction && !loading" class="msg-confirm-bar">
                <button class="msg-confirm-btn" @click="store.confirmPending(msg, route.path)">
                  ✅ 确认执行
                </button>
                <button class="msg-cancel-btn" @click="store.cancelPending()">
                  ❌ 取消
                </button>
              </div>

              <button
                v-if="msg.navigation"
                class="msg-nav-btn"
                @click="goTo(msg.navigation.route)"
              >
                <span>Go to {{ msg.navigation.label }}</span>
                <svg viewBox="0 0 20 20" width="13" height="13">
                  <path d="M4 10h12M11 5l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>

              <div v-if="msg.suggestions?.length && !loading" class="msg-suggestions">
                <button
                  v-for="(s, j) in msg.suggestions"
                  :key="j"
                  class="msg-suggestion-chip"
                  @click="ask(s)"
                >
                  {{ s }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="loading" class="msg-row assistant">
            <div class="msg-bubble msg-typing">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>
        </div>

        <footer class="chat-input-area">
          <input
            v-model="draft"
            class="chat-input"
            type="text"
            placeholder="Ask a question..."
            maxlength="2000"
            @keydown.enter="ask(draft)"
          />
          <button
            class="chat-send-btn"
            :disabled="!draft.trim() || loading"
            title="Send"
            @click="ask(draft)"
          >
            <svg viewBox="0 0 20 20" width="16" height="16">
              <path d="M3 10l14-7-4.5 7L17 17 3 10z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>
            </svg>
          </button>
        </footer>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssistantStore } from '@/stores/assistant'

const store = useAssistantStore()
const route = useRoute()
const router = useRouter()

const draft = ref('')
const messagesEl = ref<HTMLElement | null>(null)
const loading = computed(() => store.loading)

/* ---------- dragging (window + launcher) ---------- */
const WIN_W = 380
const WIN_H = 540
const LAUNCHER_SIZE = 52
const EDGE = 8

function clampPos(x: number, y: number, w: number, h: number) {
  return {
    x: Math.min(Math.max(x, EDGE), window.innerWidth - w - EDGE),
    y: Math.min(Math.max(y, EDGE), window.innerHeight - h - EDGE),
  }
}

function loadPos(key: string, fallback: { x: number; y: number }) {
  try {
    const raw = localStorage.getItem(key)
    if (raw) {
      const p = JSON.parse(raw)
      if (typeof p?.x === 'number' && typeof p?.y === 'number') return p
    }
  } catch {
    /* ignore corrupted value */
  }
  return fallback
}

const launcherPos = ref(
  loadPos('hakimi-chat-launcher-pos', {
    x: window.innerWidth - LAUNCHER_SIZE - 28,
    y: window.innerHeight - LAUNCHER_SIZE - 28,
  }),
)
const winPos = ref(
  loadPos('hakimi-chat-window-pos', {
    x: window.innerWidth - WIN_W - 28,
    y: window.innerHeight - WIN_H - 28,
  }),
)

let launcherMoved = false

function onLauncherPointerDown(e: PointerEvent) {
  launcherMoved = false
  const startX = e.clientX
  const startY = e.clientY
  const base = { ...launcherPos.value }
  const move = (ev: PointerEvent) => {
    const dx = ev.clientX - startX
    const dy = ev.clientY - startY
    if (Math.abs(dx) + Math.abs(dy) > 4) launcherMoved = true
    if (launcherMoved) {
      launcherPos.value = clampPos(base.x + dx, base.y + dy, LAUNCHER_SIZE, LAUNCHER_SIZE)
    }
  }
  const up = () => {
    window.removeEventListener('pointermove', move)
    window.removeEventListener('pointerup', up)
    localStorage.setItem('hakimi-chat-launcher-pos', JSON.stringify(launcherPos.value))
  }
  window.addEventListener('pointermove', move)
  window.addEventListener('pointerup', up)
}

function onLauncherClick() {
  if (launcherMoved) {
    // it was a drag, not a click
    launcherMoved = false
    return
  }
  store.open()
}

function onWinPointerDown(e: PointerEvent) {
  // don't start a drag from the header buttons
  if ((e.target as HTMLElement).closest('button')) return
  const startX = e.clientX
  const startY = e.clientY
  const base = { ...winPos.value }
  const move = (ev: PointerEvent) => {
    winPos.value = clampPos(base.x + ev.clientX - startX, base.y + ev.clientY - startY, WIN_W, WIN_H)
  }
  const up = () => {
    window.removeEventListener('pointermove', move)
    window.removeEventListener('pointerup', up)
    localStorage.setItem('hakimi-chat-window-pos', JSON.stringify(winPos.value))
  }
  window.addEventListener('pointermove', move)
  window.addEventListener('pointerup', up)
}

// keep the window inside the viewport when opened (e.g. after a resize)
watch(
  () => store.isOpen,
  (open) => {
    if (open) winPos.value = clampPos(winPos.value.x, winPos.value.y, WIN_W, WIN_H)
  },
)


async function ask(text: string) {
  const question = text.trim()
  if (!question) return
  draft.value = ''
  await store.ask(question, route.path)
}

function goTo(path: string) {
  router.push(path)
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

watch(
  () => [store.messages.length, store.loading, store.isOpen],
  scrollToBottom,
)

// step-by-step playback mutates the last message in place; keep scrolling
watch(
  () => store.messages,
  scrollToBottom,
  { deep: true },
)
</script>

<style scoped>
.chat-root {
  z-index: 2000;
  font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
}

/* Launcher */
.chat-launcher {
  position: fixed;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  cursor: grab;
  touch-action: none;
  color: #FBFADA;
  background: linear-gradient(135deg, #436850, #365440);
  box-shadow: 0 6px 20px rgba(67, 104, 80, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.chat-launcher:hover {
  box-shadow: 0 10px 28px rgba(67, 104, 80, 0.45);
}
.chat-launcher:active { cursor: grabbing; }

/* Window */
.chat-window {
  position: fixed;
  width: 380px;
  height: 540px;
  max-height: calc(100vh - 56px);
  display: flex;
  flex-direction: column;
  border-radius: 14px;
  overflow: hidden;
  background: #FBFADA;
  border: 1px solid rgba(173, 188, 159, 0.35);
  box-shadow: 0 16px 48px rgba(18, 55, 42, 0.22);
}

.chat-pop-enter-active,
.chat-pop-leave-active {
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: bottom right;
}
.chat-pop-enter-from,
.chat-pop-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.96);
}

/* Header */
.chat-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #12372A 0%, #2d4a38 60%, #436850 100%);
  color: #FBFADA;
  flex-shrink: 0;
  cursor: move;
  user-select: none;
  touch-action: none;
}
.chat-header-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: rgba(251, 250, 218, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.chat-header-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.chat-title { font-size: 13px; font-weight: 700; letter-spacing: 0.3px; }
.chat-subtitle { font-size: 10px; opacity: 0.65; letter-spacing: 0.4px; }
.chat-header-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: rgba(251, 250, 218, 0.8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  flex-shrink: 0;
}
.chat-header-btn:hover { background: rgba(251, 250, 218, 0.15); color: #FBFADA; }

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.chat-messages::-webkit-scrollbar { width: 5px; }
.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(67, 104, 80, 0.25);
  border-radius: 3px;
}

.msg-row { display: flex; }
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }

.msg-bubble {
  max-width: 84%;
  padding: 10px 13px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.55;
}
.msg-row.assistant .msg-bubble {
  background: #ffffff;
  color: #12372A;
  border: 1px solid rgba(173, 188, 159, 0.3);
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 4px rgba(18, 55, 42, 0.06);
}
.msg-row.user .msg-bubble {
  background: linear-gradient(135deg, #436850, #365440);
  color: #FBFADA;
  border-bottom-right-radius: 4px;
}
.msg-bubble.msg-error {
  border-color: rgba(217, 83, 79, 0.4);
  color: #D9534F;
}
.msg-text { margin: 0; white-space: pre-wrap; word-break: break-word; }

/* Step-by-step execution playback */
.msg-steps {
  list-style: none;
  margin: 0 0 8px;
  padding: 0 0 8px;
  border-bottom: 1px dashed rgba(173, 188, 159, 0.45);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.msg-step {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  font-size: 12px;
  line-height: 1.5;
  color: #2d4a38;
  animation: step-in 0.25s ease-out;
}
.msg-step-icon { flex-shrink: 0; }
.msg-step-text { flex: 1; word-break: break-word; }
@keyframes step-in {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Confirm / cancel bar for planned actions */
.msg-confirm-bar {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
.msg-confirm-btn,
.msg-cancel-btn {
  flex: 1;
  padding: 8px 0;
  font-size: 12.5px;
  font-weight: 700;
  font-family: inherit;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.msg-confirm-btn {
  color: #FBFADA;
  background: linear-gradient(135deg, #436850, #365440);
  border: none;
  box-shadow: 0 2px 8px rgba(67, 104, 80, 0.25);
}
.msg-confirm-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(67, 104, 80, 0.35); }
.msg-cancel-btn {
  color: #436850;
  background: transparent;
  border: 1px solid rgba(67, 104, 80, 0.35);
}
.msg-cancel-btn:hover { background: rgba(67, 104, 80, 0.08); }

/* Navigation button */
.msg-nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-top: 9px;
  padding: 7px 13px;
  font-size: 12px;
  font-weight: 700;
  font-family: inherit;
  color: #FBFADA;
  background: linear-gradient(135deg, #436850, #365440);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(67, 104, 80, 0.2);
}
.msg-nav-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(67, 104, 80, 0.3); }

/* Suggestion chips */
.msg-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 9px;
}
.msg-suggestion-chip {
  padding: 5px 11px;
  font-size: 11.5px;
  font-family: inherit;
  color: #436850;
  background: rgba(67, 104, 80, 0.07);
  border: 1px solid rgba(67, 104, 80, 0.22);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
}
.msg-suggestion-chip:hover {
  background: rgba(67, 104, 80, 0.14);
  border-color: rgba(67, 104, 80, 0.4);
}

/* Typing indicator */
.msg-typing { display: flex; gap: 5px; align-items: center; padding: 13px 16px; }
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ADBC9F;
  animation: bounce 1.2s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: 0.15s; }
.dot:nth-child(3) { animation-delay: 0.3s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
  30% { transform: translateY(-4px); opacity: 1; }
}

/* Input */
.chat-input-area {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #ffffff;
  border-top: 1px solid rgba(173, 188, 159, 0.3);
  flex-shrink: 0;
}
.chat-input {
  flex: 1;
  border: 1px solid rgba(173, 188, 159, 0.4);
  border-radius: 10px;
  padding: 9px 13px;
  font-size: 13px;
  font-family: inherit;
  color: #12372A;
  background: #FBFADA;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.chat-input:focus {
  border-color: #436850;
  box-shadow: 0 0 0 3px rgba(67, 104, 80, 0.12);
}
.chat-input::placeholder { color: rgba(18, 55, 42, 0.35); }
.chat-send-btn {
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  color: #FBFADA;
  background: linear-gradient(135deg, #436850, #365440);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(67, 104, 80, 0.2);
}
.chat-send-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(67, 104, 80, 0.3); }
.chat-send-btn:disabled { opacity: 0.45; cursor: not-allowed; }
</style>
