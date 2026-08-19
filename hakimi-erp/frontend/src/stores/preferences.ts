import { defineStore } from 'pinia'

export type Locale = 'zh' | 'en'
export type Theme = 'light' | 'dark'

const STORAGE_KEY = 'hakimi-erp-preferences-v1'

interface PreferencesState {
  locale: Locale
  theme: Theme
}

function readStorage(): PreferencesState {
  const fallback: PreferencesState = { locale: 'en', theme: 'light' }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return fallback
    const parsed = JSON.parse(raw)
    return {
      locale: parsed.locale === 'zh' ? 'zh' : 'en',
      theme: parsed.theme === 'dark' ? 'dark' : 'light',
    }
  } catch {
    return fallback
  }
}

export const usePreferencesStore = defineStore('preferences', {
  state: (): PreferencesState => readStorage(),
  getters: {
    isDark: (state) => state.theme === 'dark',
  },
  actions: {
    init() {
      this.apply()
    },
    setLocale(locale: Locale) {
      this.locale = locale
      this.persist()
      this.apply()
    },
    setTheme(theme: Theme) {
      this.theme = theme
      this.persist()
      this.apply()
    },
    toggleTheme() {
      this.setTheme(this.theme === 'dark' ? 'light' : 'dark')
    },
    persist() {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          locale: this.locale,
          theme: this.theme,
        }))
      } catch {
        // Ignore private-mode storage failures.
      }
    },
    apply() {
      const root = document.documentElement
      root.lang = this.locale
      root.dataset.theme = this.theme
      root.classList.toggle('dark', this.theme === 'dark')
      root.style.colorScheme = this.theme
    },
  },
})
