<template>
  <div class="page">
    <div class="header-card">
      <div class="hc-left">
        <div class="hc-icon"><svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" fill="none" stroke="currentColor" stroke-width="1.8"/></svg></div>
        <div class="hc-text"><h2 class="hc-title">{{ t('settings.title') }}</h2><p class="hc-sub">{{ t('settings.subtitle') }}</p></div>
      </div>
    </div>

    <div class="settings-grid">
      <div class="settings-card">
        <h3 class="sc-title">{{ t('settings.company') }}</h3>
        <div class="form-row form-row-2">
          <div class="form-group">
            <label class="form-label">{{ t('settings.companyName') }}</label>
            <input type="text" class="form-input" :class="{ 'is-invalid': errors.companyName }" v-model="settings.companyName" placeholder="HAKIMI Corporation" />
            <span v-if="errors.companyName" class="form-error">{{ errors.companyName }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('settings.shortName') }}</label>
            <input type="text" class="form-input" :class="{ 'is-invalid': errors.shortName }" v-model="settings.shortName" placeholder="HAKIMI" />
            <span v-if="errors.shortName" class="form-error">{{ errors.shortName }}</span>
          </div>
        </div>
        <div class="form-row form-row-2">
          <div class="form-group">
            <label class="form-label">{{ t('settings.taxId') }}</label>
            <input type="text" class="form-input" v-model="settings.taxId" placeholder="Enter tax identification number" />
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('settings.regNo') }}</label>
            <input type="text" class="form-input" v-model="settings.regNo" placeholder="Enter registration number" />
          </div>
        </div>
      </div>

      <div class="settings-card">
        <h3 class="sc-title">{{ t('settings.regional') }}</h3>
        <div class="form-row form-row-2">
          <div class="form-group">
            <label class="form-label">{{ t('settings.currency') }}</label>
            <select class="form-select" v-model="settings.currency">
              <option value="USD">USD - US Dollar</option>
              <option value="EUR">EUR - Euro</option>
              <option value="CNY">CNY - Chinese Yuan</option>
              <option value="JPY">JPY - Japanese Yen</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('settings.dateFormat') }}</label>
            <select class="form-select" v-model="settings.dateFormat">
              <option value="YYYY-MM-DD">YYYY-MM-DD (ISO)</option>
              <option value="DD/MM/YYYY">DD/MM/YYYY (EU)</option>
              <option value="MM/DD/YYYY">MM/DD/YYYY (US)</option>
            </select>
          </div>
        </div>
        <div class="form-row form-row-2">
          <div class="form-group">
            <label class="form-label">{{ t('settings.language') }}</label>
            <select class="form-select" v-model="settings.language" @change="applyPreferenceNow">
              <option value="en">English</option>
              <option value="zh">中文 (Chinese)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('settings.timezone') }}</label>
            <select class="form-select" v-model="settings.timezone">
              <option value="Asia/Shanghai">Asia/Shanghai (UTC+8)</option>
              <option value="America/New_York">America/New_York (UTC-5)</option>
              <option value="Europe/Berlin">Europe/Berlin (UTC+1)</option>
              <option value="Asia/Tokyo">Asia/Tokyo (UTC+9)</option>
            </select>
          </div>
        </div>
      </div>

      <div class="settings-card">
        <h3 class="sc-title">{{ t('settings.numbering') }}</h3>
        <div class="form-row form-row-2">
          <div class="form-group">
            <label class="form-label">{{ t('settings.soPrefix') }}</label>
            <input type="text" class="form-input" :class="{ 'is-invalid': errors.soPrefix }" v-model="settings.soPrefix" placeholder="SO" />
            <span v-if="errors.soPrefix" class="form-error">{{ errors.soPrefix }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('settings.qtPrefix') }}</label>
            <input type="text" class="form-input" :class="{ 'is-invalid': errors.qtPrefix }" v-model="settings.qtPrefix" placeholder="QT" />
            <span v-if="errors.qtPrefix" class="form-error">{{ errors.qtPrefix }}</span>
          </div>
        </div>
        <div class="form-row form-row-2">
          <div class="form-group">
            <label class="form-label">{{ t('settings.invPrefix') }}</label>
            <input type="text" class="form-input" :class="{ 'is-invalid': errors.invPrefix }" v-model="settings.invPrefix" placeholder="INV" />
            <span v-if="errors.invPrefix" class="form-error">{{ errors.invPrefix }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('settings.dlPrefix') }}</label>
            <input type="text" class="form-input" :class="{ 'is-invalid': errors.dlPrefix }" v-model="settings.dlPrefix" placeholder="DL" />
            <span v-if="errors.dlPrefix" class="form-error">{{ errors.dlPrefix }}</span>
          </div>
        </div>
      </div>

      <div class="settings-card">
        <h3 class="sc-title">{{ t('settings.preferences') }}</h3>
        <div class="form-row form-row-2">
          <div class="form-group">
            <label class="form-label">{{ t('settings.sessionTimeout') }}</label>
            <input type="number" class="form-input" :class="{ 'is-invalid': errors.sessionTimeout }" v-model.number="settings.sessionTimeout" min="5" max="480" />
            <span v-if="errors.sessionTimeout" class="form-error">{{ errors.sessionTimeout }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('settings.rowsPerPage') }}</label>
            <select class="form-select" v-model="settings.rowsPerPage">
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>
        <div class="form-row form-row-2">
          <div class="form-group">
            <label class="form-label">{{ t('settings.decimalPlaces') }}</label>
            <select class="form-select" v-model="settings.decimalPlaces">
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">{{ t('settings.theme') }}</label>
            <select class="form-select" v-model="settings.theme" @change="applyPreferenceNow">
              <option value="light">{{ t('settings.light') }}</option>
              <option value="dark">{{ t('settings.dark') }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="action-bar">
      <div class="action-left">
        <button class="btn btn-primary" @click="saveSettings">{{ t('settings.save') }}</button>
        <button class="btn btn-secondary" @click="resetSettings">{{ t('settings.reset') }}</button>
      </div>
      <span class="action-status" v-if="saved">✓ {{ t('settings.saved') }}{{ savedAt ? `${t('settings.savedAt')} ${savedAt}` : '' }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue"
import { confirm, toast } from "@/utils/toast"
import { useI18n } from "@/i18n"
import { usePreferencesStore, type Locale, type Theme } from "@/stores/preferences"

const { t } = useI18n()
const preferences = usePreferencesStore()

const STORAGE_KEY = "hakimi-erp-settings-v1"

const defaultSettings = {
  companyName: "HAKIMI Corporation",
  shortName: "HAKIMI",
  taxId: "TAX-2026-001",
  regNo: "REG-HAK-2026",
  currency: "CNY",
  dateFormat: "YYYY-MM-DD",
  language: "en" as Locale,
  timezone: "Asia/Shanghai",
  soPrefix: "SO",
  qtPrefix: "QT",
  invPrefix: "INV",
  dlPrefix: "DL",
  sessionTimeout: 30,
  rowsPerPage: "50",
  decimalPlaces: "2",
  theme: "light" as Theme,
}

type SystemSettings = typeof defaultSettings

function loadSettings(): SystemSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...defaultSettings }
    return { ...defaultSettings, ...JSON.parse(raw) }
  } catch {
    return { ...defaultSettings }
  }
}

function persistSettings() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  } catch {
    toast.warning(t("settings.unablePersist"))
  }
}

const settings = reactive<SystemSettings>(loadSettings())
const saved = ref(false)
const savedAt = ref("")
const errors = reactive<Record<string, string>>({})

function applyPreferenceNow() {
  settings.language = settings.language === "zh" ? "zh" : "en"
  settings.theme = settings.theme === "dark" ? "dark" : "light"
  preferences.setLocale(settings.language)
  preferences.setTheme(settings.theme)
  persistSettings()
}

function validateSettings(): boolean {
  for (const key of Object.keys(errors)) delete errors[key]

  if (!settings.companyName.trim()) errors.companyName = t("settings.companyName") + " " + t("settings.validation.required")
  if (!settings.shortName.trim()) errors.shortName = t("settings.shortName") + " " + t("settings.validation.required")

  const prefixes = [
    ["soPrefix", t("settings.soPrefix")],
    ["qtPrefix", t("settings.qtPrefix")],
    ["invPrefix", t("settings.invPrefix")],
    ["dlPrefix", t("settings.dlPrefix")],
  ] as const

  for (const [key, label] of prefixes) {
    const value = settings[key].trim()
    if (!value) {
      errors[key] = `${label} ${t("settings.validation.required")}`
    } else if (!/^[A-Za-z0-9]{1,10}$/.test(value)) {
      errors[key] = `${label} ${t("settings.validation.prefix")}`
    }
  }

  if (typeof settings.sessionTimeout !== "number" || settings.sessionTimeout < 5 || settings.sessionTimeout > 480) {
    errors.sessionTimeout = t("settings.validation.timeout")
  }

  return Object.keys(errors).length === 0
}

function saveSettings() {
  if (!validateSettings()) {
    toast.warning(t("settings.validation.warning"))
    return
  }

  applyPreferenceNow()
  persistSettings()
  saved.value = true
  savedAt.value = new Date().toLocaleString()
  toast.success(t("settings.saved"))

  window.setTimeout(() => {
    saved.value = false
  }, 3500)
}

async function resetSettings() {
  if (!(await confirm(t("settings.confirmReset")))) return
  Object.assign(settings, defaultSettings)
  preferences.setLocale(settings.language)
  preferences.setTheme(settings.theme)
  persistSettings()
  saved.value = true
  savedAt.value = new Date().toLocaleString()
  toast.success(t("settings.restored"))
}

onMounted(() => {
  settings.language = preferences.locale
  settings.theme = preferences.theme
})
</script>

<style scoped>
.page{padding:28px 36px;max-width:1000px;margin:0 auto;}
.header-card{display:flex;align-items:center;background:var(--app-card);border-radius:16px;padding:20px 24px;border:1px solid var(--app-border);box-shadow:0 2px 8px rgba(173,188,159,0.12);margin-bottom:20px;}
.hc-left{display:flex;align-items:center;gap:14px;}
.hc-icon{width:44px;height:44px;border-radius:12px;background:rgba(67,104,80,0.08);display:flex;align-items:center;justify-content:center;color:var(--app-primary);}
.hc-title{font-size:18px;font-weight:800;color:var(--app-text);margin:0;}
.hc-sub{font-size:12px;color:var(--app-muted);margin:2px 0 0;}

.settings-grid{display:flex;flex-direction:column;gap:16px;margin-bottom:20px;}
.settings-card{background:var(--app-card);border-radius:14px;padding:22px 24px;border:1px solid var(--app-border);box-shadow:0 2px 6px rgba(173,188,159,0.08);}
.sc-title{font-size:14px;font-weight:700;color:var(--app-primary);margin:0 0 16px;padding-bottom:10px;border-bottom:1px solid var(--app-border);display:flex;align-items:center;gap:8px;}
.sc-title::before{content:"";width:3px;height:14px;background:var(--app-primary);border-radius:2px;}

.form-row{display:grid;gap:14px;margin-bottom:14px;}
.form-row:last-child{margin-bottom:0;}
.form-row-2{grid-template-columns:1fr 1fr;}
.form-group{display:flex;flex-direction:column;gap:6px;}
.form-label{font-size:12px;font-weight:600;color:var(--app-muted);}
.form-input,.form-select{height:38px;border:1px solid var(--app-border);border-radius:8px;padding:0 12px;font-size:13px;color:var(--app-text);background:var(--app-input-bg);font-family:inherit;outline:none;transition:all 0.2s;}
.form-input:focus,.form-select:focus{border-color:var(--app-primary);box-shadow:0 0 0 3px rgba(67,104,80,0.06);}
.form-input.is-invalid{border-color:var(--app-danger);box-shadow:0 0 0 3px rgba(217,83,79,0.06);}
.form-error{font-size:11px;color:var(--app-danger);line-height:1.2;}
.form-select{cursor:pointer;appearance:none;background-image:url("data:image/svg+xml,%3Csvg viewBox=\"0 0 20 20\" width=\"12\" height=\"12\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cpath d=\"M5 7l5 5 5-5\" fill=\"none\" stroke=\"%2312372A\" stroke-width=\"1.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\" opacity=\"0.4\"/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 10px center;padding-right:32px;}

.action-bar{display:flex;align-items:center;justify-content:space-between;padding:18px 24px;background:var(--app-card);border-radius:14px;border:1px solid var(--app-border);box-shadow:0 2px 6px rgba(173,188,159,0.12);}
.action-left{display:flex;gap:12px;}
.action-status{font-size:13px;color:var(--app-primary);font-weight:600;}
.btn{display:inline-flex;align-items:center;gap:8px;padding:11px 24px;font-size:13px;font-weight:600;border-radius:8px;cursor:pointer;transition:all 0.2s;font-family:inherit;}
.btn-primary{background:linear-gradient(135deg,var(--app-primary),var(--app-primary-dark));color:var(--app-accent);border:none;box-shadow:0 2px 8px rgba(67,104,80,0.25);}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(67,104,80,0.3);}
.btn-secondary{background:rgba(173,188,159,0.2);color:var(--app-primary);border:1px solid var(--app-border);}
.btn-secondary:hover{background:rgba(173,188,159,0.3);}
</style>
