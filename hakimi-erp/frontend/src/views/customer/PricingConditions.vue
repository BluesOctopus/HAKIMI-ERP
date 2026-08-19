<template>
  <div class="page">
    <div class="header-card">
      <div class="hc-left">
        <div class="hc-icon">
          <svg viewBox="0 0 24 24" width="22" height="22">
            <circle cx="12" cy="12" r="10" fill="none" stroke="#436850" stroke-width="1.8"/>
            <path d="M12 7v5l3 2M7 12h10" fill="none" stroke="#436850" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="hc-text">
          <h2 class="hc-title">{{ isZh ? '\u5b9a\u4ef7\u6761\u4ef6' : 'Pricing Conditions' }}</h2>
          <p class="hc-sub">{{ isZh ? '\u5b9a\u4e49\u5e76\u7ef4\u62a4\u7269\u6599\u4e0e\u5ba2\u6237\u7684\u5b9a\u4ef7\u6761\u4ef6\u8bb0\u5f55\u3002' : 'Define and maintain pricing condition records for materials and customers.' }}</p>
        </div>
      </div>
    </div>
    <div v-if="loading" class="loading-msg">{{ isZh ? '\u6b63\u5728\u52a0\u8f7d\u5b9a\u4ef7\u6761\u4ef6...' : 'Loading pricing conditions...' }}</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>
    <div v-else class="data-card">
      <table class="dt">
        <thead>
          <tr>
            <th>{{ isZh ? '\u6761\u4ef6\u7c7b\u578b' : 'Cond. Type' }}</th>
            <th>{{ isZh ? '\u540d\u79f0' : 'Name' }}</th>
            <th>{{ isZh ? '\u7269\u6599' : 'Material' }}</th>
            <th>{{ isZh ? '\u5ba2\u6237' : 'Customer' }}</th>
            <th class="num">{{ isZh ? '\u91d1\u989d' : 'Amount' }}</th>
            <th>{{ isZh ? '\u5e01\u79cd' : 'Crcy' }}</th>
            <th>{{ isZh ? '\u6709\u6548\u671f\u81ea' : 'Valid From' }}</th>
            <th>{{ isZh ? '\u6709\u6548\u671f\u81f3' : 'Valid To' }}</th>
            <th>{{ isZh ? '\u72b6\u6001' : 'Status' }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.conditionId" class="dr">
            <td class="mono">{{ r.conditionType }}</td>
            <td>{{ r.conditionName }}</td>
            <td class="mono">{{ r.materialId || '*' }}</td>
            <td>{{ r.bpId || '*' }}</td>
            <td class="num mono">{{ r.amount || (r.rate ? r.rate + '%' : '-') }}</td>
            <td>{{ r.currency }}</td>
            <td>{{ r.validFrom }}</td>
            <td>{{ r.validTo }}</td>
            <td><span class="stag" :class="r.status==='ACTIVE'?'s-done':'s-cancel'">{{ r.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePreferencesStore } from '@/stores/preferences'
import { fetchPricingConditions } from '@/api'

const preferences = usePreferencesStore()
const isZh = computed(() => preferences.locale === 'zh')
const rows = ref<any[]>([])
const loading = ref(true)
const error = ref('')
onMounted(async () => {
  try {
    const data = await fetchPricingConditions({ pageSize: 100 })
    rows.value = data.items || []
  } catch (e: any) { error.value = e.message || 'Failed to load pricing conditions' }
  finally { loading.value = false }
})
</script>

<style scoped>
.page{padding:28px 36px;max-width:1200px;margin:0 auto;}
.header-card{display:flex;align-items:center;background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:16px;padding:20px 24px;border:1px solid rgba(173,188,159,0.18);box-shadow:0 2px 8px rgba(173,188,159,0.12);margin-bottom:20px;}
.hc-left{display:flex;align-items:center;gap:14px;}
.hc-icon{width:44px;height:44px;border-radius:12px;background:rgba(67,104,80,0.08);display:flex;align-items:center;justify-content:center;}
.hc-title{font-size:18px;font-weight:800;color:#12372A;margin:0;}
.hc-sub{font-size:12px;color:rgba(18,55,42,0.45);margin:2px 0 0;}
.loading-msg,.error-msg{text-align:center;padding:40px;color:rgba(18,55,42,0.4);font-size:14px;}
.error-msg{color:#D9534F;}
.data-card{background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:14px;border:1px solid rgba(173,188,159,0.15);box-shadow:0 2px 6px rgba(173,188,159,0.1);overflow:hidden;}
.dt{width:100%;border-collapse:collapse;font-size:13px;}
.dt th{text-align:left;padding:12px 14px;font-size:10px;font-weight:700;color:rgba(18,55,42,0.45);text-transform:uppercase;letter-spacing:0.8px;background:rgba(173,188,159,0.08);border-bottom:1px solid rgba(173,188,159,0.2);}
.dt th.num{text-align:right;}
.dt td{padding:11px 14px;border-bottom:1px solid rgba(173,188,159,0.08);color:#12372A;}
.dt td.num{text-align:right;}
.dr:hover{background:rgba(67,104,80,0.025);}
.mono{font-family:'SF Mono',Consolas,monospace;font-size:12px;}
.stag{font-size:10px;font-weight:600;padding:3px 8px;border-radius:5px;}
.s-done{background:rgba(67,104,80,0.1);color:#436850;}
.s-cancel{background:rgba(217,83,79,0.08);color:#c94a45;}
</style>
