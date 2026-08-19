import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import '@/assets/styles/global.css'
import App from './App.vue'
import router from './router'
import { usePreferencesStore } from '@/stores/preferences'
import { startDomTranslator } from '@/i18n/domTranslator'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

usePreferencesStore(pinia).init()

app.mount('#app')
startDomTranslator()
