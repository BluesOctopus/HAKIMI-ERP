<template>
  <div class="home-page">
    <section class="hero-section">
        <div class="hero-left">
          <span class="hero-badge">SAP SD Simplified</span>
          <h2 class="hero-title">
            <span class="title-line title-line-1">Welcome to</span>
            <span class="title-line title-line-2">HAKIMI ERP</span>
          </h2>
          <p class="hero-desc">
            Streamline your sales and distribution operations with an intuitive,
            enterprise-grade management platform built for modern teams.
          </p>
          <button class="cta-btn" @click="scrollToOverview">
            <span>Go to Dashboard</span>
            <svg viewBox="0 0 20 20" width="16" height="16">
              <path d="M4 10h12M11 5l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        <div class="hero-right">
          <div class="illustration">
            <div class="illu-monitor">
              <div class="illu-screen">
                <div class="illu-dashboard">
                  <div class="illu-sidebar"></div>
                  <div class="illu-main">
                    <div class="illu-topbar"></div>
                    <div class="illu-chart-area">
                      <div class="illu-bars">
                        <div class="illu-bar" style="height:50%"></div>
                        <div class="illu-bar" style="height:75%"></div>
                        <div class="illu-bar active" style="height:35%"></div>
                        <div class="illu-bar active" style="height:88%"></div>
                        <div class="illu-bar" style="height:60%"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="illu-stand"></div>
              <div class="illu-base"></div>
            </div>
            <div class="illu-float float-gear">
              <svg viewBox="0 0 40 40" width="40" height="40">
                <path d="M20 6l3 2 3.5-1.2 1.2 3.5 3.5 1.2-1.2 3.5 2 3-3.5 1.2-1.2 3.5-3.5-1.2-3 2-1.2-3.5-3.5-1.2 1.2-3.5-2-3 3.5-1.2 1.2-3.5z" fill="none" stroke="#436850" stroke-width="1.8"/>
                <circle cx="20" cy="20" r="4" fill="#436850"/>
              </svg>
            </div>
            <div class="illu-float float-check">
              <svg viewBox="0 0 32 32" width="28" height="28">
                <circle cx="16" cy="16" r="13" fill="#ADBC9F" opacity="0.22"/>
                <path d="M9 16l5 5 9-9" fill="none" stroke="#436850" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
      </section>

      <section class="kpi-section">
        <div class="section-header">
          <svg viewBox="0 0 20 20" width="18" height="18" class="section-icon">
            <rect x="2" y="2" width="16" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <path d="M6 14l3-4 2 2 3-5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <h3 class="section-title">Overview</h3>
        </div>
        <div v-if="loading" class="cards-skeleton">
          <div v-for="i in 5" :key="i" class="skeleton-card"></div>
        </div>
        <div v-else-if="error" class="error-msg">{{ error }}</div>
        <div v-else class="cards-grid">
          <IndicatorCard v-for="card in cards" :key="card.title"
            :title="card.title"
            :value="card.value"
            :change="card.change"
            :change-type="card.changeType"
            :comparison="card.comparison"
            :color="card.color"
            :icon="card.icon"
          />
        </div>
      </section>

      <section class="assistant-section">
        <div class="assistant-banner">
          <div class="assistant-icon-wrap">
            <svg viewBox="0 0 52 52" width="52" height="52">
              <circle cx="22" cy="22" r="20" fill="#436850" opacity="0.08"/>
              <circle cx="22" cy="18" r="9" fill="none" stroke="#436850" stroke-width="1.8"/>
              <path d="M14 29c0-4.4 3.6-8 8-8s8 3.6 8 8" fill="none" stroke="#436850" stroke-width="1.8" stroke-linecap="round"/>
              <circle cx="19" cy="17" r="1.3" fill="#436850"/>
              <circle cx="25" cy="17" r="1.3" fill="#436850"/>
              <path d="M18 23h8" fill="none" stroke="#436850" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="assistant-content">
            <p class="assistant-headline">Let's work smarter, together.</p>
            <p class="assistant-desc">Need help with order processing, delivery tracking, or financial reports? The AI assistant is ready to guide you through every workflow.</p>
          </div>
          <button class="assistant-cta" @click="assistantStore.open()">Ask a question</button>
        </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import IndicatorCard from '@/components/IndicatorCard.vue'
import { fetchDashboardSummary } from '@/api/modules/report'
import { formatCurrency, formatNumber } from '@/utils/format'
import { useAssistantStore } from '@/stores/assistant'

const assistantStore = useAssistantStore()

const loading = ref(true)
const error = ref('')
const summary = ref<any>(null)

function scrollToOverview() {
  const el = document.querySelector('.kpi-section')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

const cards = computed(() => {
  if (!summary.value) return []
  
  return [
    {
      title: 'Sales Orders',
      value: formatNumber(summary.value.salesOrders.value, 0),
      change: summary.value.salesOrders.change,
      changeType: summary.value.salesOrders.type as 'up' | 'down',
      comparison: summary.value.salesOrders.comparison,
      color: '#436850',
      icon: '<path d="M4 4h3l1 5h7l2-5h2M7 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm7 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
    },
    {
      title: 'Delivery Orders',
      value: formatNumber(summary.value.deliveryOrders.value, 0),
      change: summary.value.deliveryOrders.change,
      changeType: summary.value.deliveryOrders.type as 'up' | 'down',
      comparison: summary.value.deliveryOrders.comparison,
      color: '#436850',
      icon: '<rect x="2" y="3" width="16" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2 8h16M6 13h2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
    },
    {
      title: 'Pending Deliveries',
      value: formatNumber(summary.value.pendingDeliveries.value, 0),
      change: summary.value.pendingDeliveries.change,
      changeType: summary.value.pendingDeliveries.type as 'up' | 'down',
      comparison: summary.value.pendingDeliveries.comparison,
      color: '#F0AD4E',
      icon: '<circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 6v4l3 2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
    },
    {
      title: 'Receivables',
      value: formatCurrency(summary.value.receivables.value, 'CNY'),
      change: summary.value.receivables.change,
      changeType: summary.value.receivables.type as 'up' | 'down',
      comparison: summary.value.receivables.comparison,
      color: '#436850',
      icon: '<circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 5v3M7 8l3-3 3 3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M10 12c3 0 5-2 5-5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
    },
    {
      title: 'This Month Profit',
      value: formatCurrency(summary.value.monthProfit.value, 'CNY'),
      change: summary.value.monthProfit.change,
      changeType: summary.value.monthProfit.type as 'up' | 'down',
      comparison: summary.value.monthProfit.comparison,
      color: '#D9534F',
      icon: '<rect x="2" y="3" width="16" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 11l3 3 4-7" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
    },
  ]
})

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    summary.value = await fetchDashboardSummary()
  } catch (err: any) {
    error.value = err?.message || 'Failed to load dashboard data'
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

<style scoped>
.home-page {
  padding: 36px 48px 24px;
  max-width: 1280px;
  margin: 0 auto;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

/* Hero */
.hero-section {
  display: flex;
  align-items: center;
  gap: 40px;
  margin-bottom: 36px;
}
.hero-left { flex: 1; max-width: 500px; }
.hero-right { flex: 0 0 320px; display: flex; justify-content: center; }

.hero-badge {
  display: inline-block; font-size: 10px; font-weight: 700; color: #436850;
  background: rgba(67, 104, 80, 0.1); padding: 5px 14px; border-radius: 20px;
  letter-spacing: 2px; text-transform: uppercase; margin-bottom: 18px;
  border: 1px solid rgba(67, 104, 80, 0.12);
}

.hero-title { margin: 0 0 18px; line-height: 1.1; }
.title-line { display: block; font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif; }
.title-line-1 { font-size: 20px; font-weight: 300; color: rgba(18, 55, 42, 0.45); letter-spacing: 4px; text-transform: uppercase; }
.title-line-2 {
  font-size: 54px; font-weight: 900; letter-spacing: -2px;
  background: linear-gradient(135deg, #12372A 0%, #436850 45%, #2d4a38 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.title-line-2::after {
  content: ''; position: absolute; bottom: 4px; left: 0; width: 100%; height: 2px;
  background: linear-gradient(90deg, #436850 0%, transparent 100%); border-radius: 1px;
}

.hero-desc { font-size: 14px; color: rgba(18, 55, 42, 0.5); margin: 0 0 28px; line-height: 1.7; max-width: 400px; }

.cta-btn {
  display: inline-flex; align-items: center; gap: 10px;
  background: linear-gradient(135deg, #436850, #365440); color: #FBFADA;
  border: none; border-radius: 12px; padding: 14px 30px; font-size: 14px; font-weight: 700;
  cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif; letter-spacing: 0.5px;
  box-shadow: 0 4px 16px rgba(67, 104, 80, 0.25);
}
.cta-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(67, 104, 80, 0.35); }

/* Illustration - ENLARGED */
.illustration { position: relative; width: 300px; height: 260px; }
.illu-monitor { position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%); }
.illu-screen {
  width: 180px; height: 118px;
  background: linear-gradient(145deg, #ffffff, #FBFADA);
  border: 3px solid #12372A; border-radius: 10px; padding: 6px;
  display: flex; overflow: hidden;
  box-shadow: 0 10px 24px rgba(18, 55, 42, 0.1);
}
.illu-dashboard { display: flex; width: 100%; gap: 3px; }
.illu-sidebar { width: 18px; background: #12372A; border-radius: 2px; flex-shrink: 0; opacity: 0.9; }
.illu-main { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.illu-topbar { height: 11px; background: rgba(18,55,42,0.05); border-radius: 2px; }
.illu-chart-area { flex: 1; display: flex; align-items: flex-end; padding: 3px 2px; }
.illu-bars { display: flex; align-items: flex-end; gap: 2px; width: 100%; height: 100%; }
.illu-bar { flex: 1; background: rgba(173,188,159,0.3); border-radius: 1px 1px 0 0; }
.illu-bar.active { background: #436850; }
.illu-stand { width: 36px; height: 22px; background: linear-gradient(180deg, #12372A, #0d291f); margin: 0 auto; border-radius: 0 0 2px 2px; }
.illu-base { width: 72px; height: 5px; background: #12372A; border-radius: 3px; margin: 0 auto; }

.illu-float { position: absolute; animation: float 3.5s ease-in-out infinite; }
.float-gear { top: 6px; right: 20px; }
.float-check { top: 60px; right: 60px; animation-delay: 1.8s; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }

/* KPI */
.kpi-section { margin-bottom: 24px; }
.section-header { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; }
.section-icon { color: #436850; }
.section-title { font-size: 15px; font-weight: 700; color: #12372A; margin: 0; letter-spacing: -0.2px; }
.cards-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 18px; }
.cards-skeleton { display: grid; grid-template-columns: repeat(5, 1fr); gap: 18px; }
.skeleton-card {
  height: 108px;
  border-radius: 14px;
  background: linear-gradient(90deg, rgba(173,188,159,0.15) 25%, rgba(173,188,159,0.25) 50%, rgba(173,188,159,0.15) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.error-msg { color: #D9534F; font-size: 14px; padding: 12px 0; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* Assistant - TALLER */
.assistant-section { margin-top: auto; padding-top: 12px; }
.assistant-banner {
  display: flex; align-items: center; gap: 24px;
  background: linear-gradient(135deg, rgba(67, 104, 80, 0.04), rgba(173, 188, 159, 0.06));
  border: 1px solid rgba(173, 188, 159, 0.2);
  border-radius: 14px;
  padding: 36px 32px;
}
.assistant-icon-wrap { flex-shrink: 0; }
.assistant-content { flex: 1; }
.assistant-headline { font-size: 16px; font-weight: 700; color: #12372A; margin: 0 0 6px; }
.assistant-desc { font-size: 13px; color: rgba(18, 55, 42, 0.45); margin: 0; line-height: 1.6; }
.assistant-cta {
  background: linear-gradient(135deg, #436850, #365440); color: #FBFADA;
  border: none; border-radius: 10px; padding: 12px 24px; font-size: 13px; font-weight: 700;
  cursor: pointer; white-space: nowrap; transition: all 0.25s;
  font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif; letter-spacing: 0.3px;
  box-shadow: 0 2px 10px rgba(67, 104, 80, 0.2);
}
.assistant-cta:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(67, 104, 80, 0.3); }
</style>