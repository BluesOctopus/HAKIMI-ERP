<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-logo">
      <div class="logo-mark">
        <svg viewBox="0 0 36 36" width="30" height="30">
          <defs>
            <linearGradient id="logoGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#436850"/>
              <stop offset="100%" stop-color="#2d4a38"/>
            </linearGradient>
          </defs>
          <rect width="36" height="36" rx="8" fill="url(#logoGrad)"/>
          <text x="18" y="25" text-anchor="middle" fill="#FBFADA" font-size="20" font-weight="700" font-family="Inter,sans-serif">H</text>
        </svg>
      </div>
      <transition name="fade">
        <span v-show="!isCollapsed" class="logo-text">HAKIMI</span>
      </transition>
    </div>

    <nav class="sidebar-nav">
      <!-- Home -->
      <ul class="nav-list">
        <RouterLink to="/" custom v-slot="{ navigate, isActive }">
          <li class="nav-item" :class="{ active: isActive }" @click="navigate">
            <svg class="nav-icon" viewBox="0 0 20 20" width="18" height="18" style="pointer-events: none;">
              <path d="M3 10l7-7 7 7M5 8v7a1 1 0 0 0 1 1h3v-4h2v4h3a1 1 0 0 0 1-1V8" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span v-show="!isCollapsed" class="nav-text" style="pointer-events: none;">Home</span>
          </li>
        </RouterLink>
      </ul>

      <div class="nav-divider" v-show="!isCollapsed"></div>

      <!-- Collapsible Menu Sections -->
      <div class="nav-section" v-for="section in menuItems" :key="section.label">
        <button
          class="section-header"
          @click="toggleSection(section.label)"
          :class="{ expanded: expandedSections.has(section.label) }"
        >
          <svg class="section-icon" viewBox="0 0 20 20" width="18" height="18" v-html="section.icon" style="pointer-events: none;"></svg>
          <div class="section-label-wrap" v-show="!isCollapsed" style="pointer-events: none;">
            <span class="section-label">{{ displayLabel(section.label) }}</span>
          </div>
          <svg v-show="!isCollapsed" class="section-chevron" viewBox="0 0 16 16" width="12" height="12" style="pointer-events: none;">
            <path d="M5 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <transition name="expand">
          <ul v-show="expandedSections.has(section.label) && !isCollapsed" class="nav-list sub-list">
            <RouterLink v-for="item in section.children" :key="item.path"
                :to="item.path"
                custom
                v-slot="{ navigate, isActive }">
              <li class="nav-item nav-sub-item"
                  :class="{ active: isActive }"
                  @click="navigate">
                <div class="nav-item-inner">
                  <svg class="nav-icon nav-sub-icon" viewBox="0 0 20 20" width="16" height="16" v-html="item.icon"></svg>
                  <span class="nav-text nav-sub-text">{{ displayLabel(item.label) }}</span>
                </div>
              </li>
            </RouterLink>
          </ul>
        </transition>
      </div>
    </nav>

    <div class="sidebar-footer">
      <button class="collapse-btn" @click="toggleCollapse">
        <svg viewBox="0 0 20 20" width="14" height="14" :style="{ transform: isCollapsed ? 'rotate(180deg)' : 'none' }">
          <path fill="none" d="M12 4l-6 6 6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { usePreferencesStore } from '@/stores/preferences'

const route = useRoute()
const router = useRouter()
const preferences = usePreferencesStore()
const isCollapsed = ref(false)
const currentPath = computed(() => route.path)
const expandedSections = reactive(new Set<string>())

interface MenuItem { path: string; label: string; icon: string }
interface MenuSection { label: string; icon: string; children: MenuItem[] }

const navLabelMap: Record<string, string> = {
  'Home': '首页',
  'Customer\nManagement': '客户管理',
  'Business Partner': '业务伙伴',
  'Material': '物料主数据',
  'Product': '产品',
  'Pricing Conditions': '定价条件',
  'Sales Organization': '销售组织',
  'Sales\nManagement': '销售管理',
  'Inquiry': '询价管理',
  'Quotation Management': '报价管理',
  'Sales Orders': '销售订单',
  'Delivery\nManagement': '配送管理',
  'Delivery List': '发货单列表',
  'Status Monitoring': '配送状态监控',
  'Financial Management': '财务管理',
  'Invoice Management': '发票管理',
  'Invoice': '发票',
  'Receivables Management': '应收管理',
  'Receivables': '应收',
  'Unpaid Receivables': '未收应收',
  'Report\nQuery': '报表查询',
  'System\nSettings': '系统设置',
}

function displayLabel(label: string): string {
  if (preferences.locale !== 'zh') return label
  return navLabelMap[label] || label
}


const menuItems: MenuSection[] = [
  {
    label: 'Customer\nManagement',
    icon: '<circle cx="10" cy="7" r="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M4 17c0-3.3 2.7-6 6-6s6 2.7 6 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
    children: [
      { path: '/customer/bp', label: 'Business Partner', icon: '<circle cx="10" cy="7" r="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M4 17c0-3.3 2.7-6 6-6s6 2.7 6 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
      { path: '/customer/material', label: 'Material', icon: '<rect x="2" y="2" width="7" height="7" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="11" y="2" width="7" height="7" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="2" y="11" width="7" height="7" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="11" y="11" width="7" height="7" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/>' },
      { path: '/customer/product', label: 'Product', icon: '<path d="M10 2l6 4v8l-6 4-6-4V6l6-4z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M10 6v8M4 8l6 4 6-4" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>' },
      { path: '/customer/pricing', label: 'Pricing Conditions', icon: '<circle cx="10" cy="10" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 6v4l3 2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>' },
      { path: '/customer/salesorg', label: 'Sales Organization', icon: '<path d="M3 17V7a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M7 9h6M7 13h4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
    ]
  },
  {
    label: 'Sales\nManagement',
    icon: '<path d="M4 4h3l1 5h7l2-5h2M7 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm7 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
    children: [
      { path: '/sales/inquiry', label: 'Inquiry', icon: '<path d="M6 3h8l4 4v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M14 3v4h4M7 10h6M7 14h4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
      { path: '/sales/quotation', label: 'Quotation Management', icon: '<path d="M5 3h10l4 4v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M13 3v4h4M7 11l2 2 4-4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>' },
      { path: '/sales/orders', label: 'Sales Orders', icon: '<path d="M4 4h3l1 5h7l2-5h2M7 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm7 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>' },
    ]
  },
  {
    label: 'Delivery\nManagement',
    icon: '<rect x="2" y="3" width="16" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2 8h16M6 13h2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
    children: [
      { path: '/delivery/list', label: 'Delivery List', icon: '<rect x="2" y="3" width="16" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2 8h16M6 13h2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
      { path: '/delivery/monitor', label: 'Status Monitoring', icon: '<rect x="2" y="2" width="16" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 14l3-4 2 2 3-5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>' },
    ]
  },
  {
    label: 'Financial Management',
    icon: '<rect x="2" y="4" width="16" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2 8h16M6 12h3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
    children: [
      { path: '/finance/invoice', label: 'Invoice', icon: '<rect x="2" y="4" width="16" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2 8h16M6 12h3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
      { path: '/finance/receivables', label: 'Receivables', icon: '<circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 10h8M10 6v8" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
      { path: '/finance/unpaid', label: 'Unpaid Receivables', icon: '<circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 6v4l-3 3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>' },
    ]
  },
  {
    label: 'Report\nQuery',
    icon: '<rect x="2" y="2" width="16" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 14l3-4 2 2 3-5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
    children: [
      { path: '/report', label: 'Report Query', icon: '<rect x="2" y="2" width="16" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 14l3-4 2 2 3-5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>' },
    ]
  },
  {
    label: 'System\nSettings',
    icon: '<circle cx="10" cy="10" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.9 4.9l1.4 1.4M13.7 13.7l1.4 1.4M4.9 15.1l1.4-1.4M13.7 6.3l1.4-1.4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
    children: [
      { path: '/settings', label: 'System Settings', icon: '<circle cx="10" cy="10" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.9 4.9l1.4 1.4M13.7 13.7l1.4 1.4M4.9 15.1l1.4-1.4M13.7 6.3l1.4-1.4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>' },
    ]
  },
]

function toggleSection(label: string) {
  if (expandedSections.has(label)) { expandedSections.delete(label) }
  else { expandedSections.add(label) }
}

function autoExpandCurrent() {
  for (const section of menuItems) {
    if (section.children.some(item => item.path === currentPath.value)) {
      expandedSections.add(section.label)
    }
  }
}
watch(currentPath, () => autoExpandCurrent(), { immediate: true })

function toggleCollapse() { isCollapsed.value = !isCollapsed.value }
</script>

<style scoped>
.sidebar {
  width: 230px;
  background-color: rgba(18, 55, 42, 0.98);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #FBFADA;
  display: flex;
  flex-direction: column;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  flex-shrink: 0;
  border-right: 1px solid rgba(67, 104, 80, 0.25);
  position: relative;
  z-index: 1000;
}
.sidebar.collapsed { width: 60px; }

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 15px;
  border-bottom: 1px solid rgba(251, 250, 218, 0.06);
}
.logo-mark { flex-shrink: 0; }
.logo-text { font-size: 18px; font-weight: 800; letter-spacing: 2px; color: #FBFADA; white-space: nowrap; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0 12px;
}
.sidebar-nav::-webkit-scrollbar { width: 3px; }
.sidebar-nav::-webkit-scrollbar-thumb { background: rgba(251,250,218,0.1); border-radius: 2px; }

.nav-list { list-style: none; padding: 0; margin: 0; }
.nav-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(251,250,218,0.08), transparent);
  margin: 4px 14px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 18px;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 0 24px 24px 0;
  margin: 1px 10px 1px 0;
  color: rgba(251, 250, 218, 0.6);
  position: relative;
  z-index: 10;
}
.nav-item:hover { background-color: rgba(67, 104, 80, 0.3); color: rgba(251, 250, 218, 0.9); }
.nav-item.active { background-color: rgba(67, 104, 80, 0.7); color: #FBFADA; font-weight: 500; }
.nav-icon { flex-shrink: 0; opacity: 0.75; }
.nav-item.active .nav-icon { opacity: 1; }
.nav-text { font-size: 13px; white-space: nowrap; }

/* Section Header */
.nav-section { margin: 2px 0; }

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  width: calc(100% - 10px);
  padding: 10px 16px;
  margin: 1px 8px 1px 0;
  border: none;
  border-radius: 0 20px 20px 0;
  background: transparent;
  color: rgba(251, 250, 218, 0.5);
  font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
  cursor: pointer;
  transition: all 0.25s;
  text-align: left;
}
.section-header:hover {
  color: rgba(251, 250, 218, 0.8);
  background: rgba(67, 104, 80, 0.15);
}
.section-header.expanded {
  color: rgba(251, 250, 218, 0.7);
  background: rgba(67, 104, 80, 0.1);
}

.section-icon {
  flex-shrink: 0;
  opacity: 0.7;
  color: rgba(251, 250, 218, 0.7);
}
.section-header.expanded .section-icon { opacity: 0.9; }

.section-label-wrap { flex: 1; min-width: 0; }
.section-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  white-space: pre-line;
  line-height: 1.35;
}

.section-chevron {
  flex-shrink: 0;
  opacity: 0.4;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.section-header.expanded .section-chevron { transform: rotate(90deg); opacity: 0.7; }

/* Sub-items */
.sub-list { padding: 2px 0 6px; overflow: hidden; }
.nav-item-inner {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}
.nav-sub-item { padding: 7px 18px 7px 44px; font-size: 12px; color: rgba(251, 250, 218, 0.45); }
.nav-sub-item:hover { color: rgba(251, 250, 218, 0.85); background: rgba(67, 104, 80, 0.2); }
.nav-sub-item.active { color: #FBFADA; background: rgba(67, 104, 80, 0.6); font-weight: 500; }
.nav-sub-icon { opacity: 0.5; flex-shrink: 0; }
.nav-sub-item.active .nav-sub-icon { opacity: 1; }
.nav-sub-text { font-size: 12px; }

/* Expand Transition */
.expand-enter-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); overflow: hidden; }
.expand-leave-active { transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); overflow: hidden; }
.expand-enter-from, .expand-leave-to { opacity: 0; max-height: 0; transform: translateY(-4px); }
.expand-enter-to, .expand-leave-from { opacity: 1; max-height: 300px; transform: translateY(0); }

/* Footer */
.sidebar-footer { border-top: 1px solid rgba(251, 250, 218, 0.06); padding: 10px; }
.collapse-btn {
  background: none; border: none; color: rgba(251, 250, 218, 0.3);
  cursor: pointer; padding: 8px; display: flex; align-items: center;
  justify-content: center; width: 100%; border-radius: 8px; transition: all 0.2s;
}
.collapse-btn:hover { color: rgba(251, 250, 218, 0.65); background: rgba(67, 104, 80, 0.2); }
.collapse-btn svg { transition: transform 0.3s; }

.assistant-entry {
  display: flex; align-items: center; gap: 10px; padding: 10px 8px;
  cursor: pointer; border-radius: 8px; transition: background-color 0.2s;
}
.assistant-entry:hover { background-color: rgba(67, 104, 80, 0.25); }
.assistant-icon { opacity: 0.4; }
.assistant-label { font-size: 12px; color: rgba(251, 250, 218, 0.4); }
</style>
