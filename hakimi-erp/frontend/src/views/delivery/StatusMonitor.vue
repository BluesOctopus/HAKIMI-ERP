<template>
  <div class="page">
    <div class="header-card">
        <div class="hc-left">
          <div class="hc-icon"><svg viewBox="0 0 24 24" width="22" height="22"><rect x="2" y="5" width="20" height="13" rx="2" fill="none" stroke="#436850" stroke-width="1.8"/><path d="M6 5V3M18 5V3M2 11h20M7 16h3" fill="none" stroke="#436850" stroke-width="1.5" stroke-linecap="round"/></svg></div>
          <div class="hc-text"><h2 class="hc-title">{{ isZh ? '\u914d\u9001\u72b6\u6001\u76d1\u63a7' : 'Delivery Status Monitoring' }}</h2><p class="hc-sub">{{ isZh ? '\u5b9e\u65f6\u76d1\u63a7\u914d\u9001\u8fdb\u5ea6\uff0c\u6bcf\u7b14\u8ba2\u5355\u72b6\u6001\u4e00\u76ee\u4e86\u7136\u3002' : 'Monitor delivery progress in real time. The status of each order is clear at a glance.' }}</p></div>
        </div>
        <div class="hc-right">
          <label class="auto-refresh"><input type="checkbox" v-model="ar" /> Auto Refresh</label>
          <select class="form-select form-select-sm" v-model="ri"><option>30s</option><option>60s</option><option>5min</option></select>
        </div>
      </div>

      <div class="filter-bar">
        <input type="text" class="form-input" v-model="f.dn" :placeholder="isZh ? '\u53d1\u8d27\u5355\u53f7' : 'Delivery No.'" />
        <input type="text" class="form-input" v-model="f.sn" :placeholder="isZh ? '\u9500\u552e\u8ba2\u5355\u53f7' : 'Sales Order No.'" />
        <input type="text" class="form-input" v-model="f.cn" :placeholder="isZh ? '\u5ba2\u6237\u540d\u79f0' : 'Customer Name'" />
        <select class="form-select" v-model="f.st"><option value="">{{ isZh ? '\u5168\u90e8\u72b6\u6001' : 'All Statuses' }}</option><option>{{ isZh ? '\u521b\u5efa\u4e2d' : 'Creating' }}</option><option>{{ isZh ? '\u62e3\u914d\u4e2d' : 'Picking' }}</option><option>{{ isZh ? '\u5df2\u62e3\u914d' : 'Picked' }}</option><option>{{ isZh ? '\u8fd0\u8f93\u4e2d' : 'In Transit' }}</option><option>{{ isZh ? '\u5df2\u5b8c\u6210' : 'Completed' }}</option><option>{{ isZh ? '\u5df2\u53d6\u6d88' : 'Cancelled' }}</option></select>
        <button class="btn btn-primary" @click="search" :disabled="loading">{{ isZh ? '\u67e5\u8be2' : 'Search' }}</button>
        <button class="btn btn-outline" @click="reset" :disabled="loading">{{ isZh ? '\u91cd\u7f6e' : 'Reset' }}</button>
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <div class="data-card">
        <div class="table-scroll"><table class="data-table">
          <thead><tr>
            <th class="sticky-left">Del. No.</th><th>{{ isZh ? '\u9500\u552e\u8ba2\u5355' : 'Sales Order' }}</th><th>{{ isZh ? '\u5ba2\u6237' : 'Customer' }}</th><th>{{ isZh ? '\u8ba1\u5212\u53d1\u8d27\u8fc7\u8d26' : 'Planned GI' }}</th><th>{{ isZh ? '\u72b6\u6001' : 'Status' }}</th>
            <th class="prog-hdr">{{ isZh ? '\u8fdb\u5ea6' : 'Progress' }}</th><th class="num qty-hdr">{{ isZh ? '\u6570\u91cf\uff08\u5df2\u62e3\u002f\u603b\u8ba1\uff09' : 'Qty (Pick/Total)' }}</th><th>{{ isZh ? '\u64cd\u4f5c' : 'Action' }}</th>
          </tr></thead>
          <tbody>
            <tr v-if="loading && displayedRows.length === 0"><td colspan="9" class="empty-cell">{{ isZh ? '\u6b63\u5728\u52a0\u8f7d\u53d1\u8d27\u5355\u002e\u002e\u002e' : 'Loading deliveries...' }}</td></tr>
            <tr v-for="row in displayedRows" :key="row.id" class="data-row">
              <td class="sticky-left mono">{{ row.dn }}</td><td class="mono">{{ row.sn }}</td><td>{{ row.cn }}</td><td>{{ row.gi }}</td>
              <td><span class="stag" :class="sc(row.st)">{{ row.st }}</span></td>
              <td class="prog-hdr"><div class="ms-bar">
                <div v-for="(m,i) in milestones" :key="i" class="ms-step">
                  <div class="ms-dot" :class="{done:row.si>=i,cur:row.si===i}"></div>
                  <div v-if="i < milestones.length - 1" class="ms-line" :class="{done:row.si>i}"></div>
                  <span class="ms-lbl">{{ m }}</span>
                </div>
              </div></td>
              <td class="num mono qty-cell">{{ row.dt }}</td>
              <td>
                <div class="row-actions">
                  <a class="link" @click="$router.push('/delivery/detail/'+row.id)">{{ isZh ? '\u67e5\u770b\u8be6\u60c5' : 'View Details' }}</a>
                  <a v-if="row.actionLabel" class="link pgi-link" :class="{disabled: postingId === row.id}" @click="processDelivery(row)">
                    {{ postingId === row.id ? 'Processing...' : row.actionLabel }}
                  </a>
                </div>
              </td>
            </tr>
            <tr v-if="!loading && displayedRows.length === 0"><td colspan="9" class="empty-cell">{{ isZh ? '\u672a\u627e\u5230\u53d1\u8d27\u5355\u3002' : 'No deliveries found.' }}</td></tr>
          </tbody>
        </table></div>
        <div class="table-footer">
          <div class="tf-left"><span class="tf-total">Total {{ pagination.total }} items</span><select class="form-select form-select-sm" style="width:80px"><option>10 / page</option><option>20</option><option>50</option></select></div>
          <div class="pager"><button v-for="p in Math.min(pagination.totalPages, 5)" :key="p" class="pg-btn" :class="{active: p === currentPage}" @click="goPage(p)">{{ p }}</button></div>
          <div class="tf-right"><span class="tf-label">Go to</span><input type="text" class="pg-input" placeholder="page" /></div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { usePreferencesStore } from '@/stores/preferences'
import { alert, confirm } from '@/utils/toast'
import { confirmPicking, fetchDeliveries, postGoodsIssue, shipDelivery, startPicking } from '@/api/modules/logistics'
import type { DeliveryListItem } from '@/api/modules/logistics'
import { fetchPartners } from '@/api/modules/master'
import type { Partner } from '@/api/modules/master'

const router = useRouter()
const preferences = usePreferencesStore()
const isZh = computed(() => preferences.locale === 'zh')
const ar = ref(false)
const ri = ref('30s')
const f = reactive({ dn: '', sn: '', cn: '', st: '' })

const rawItems = ref<DeliveryListItem[]>([])
const partnerMap = ref<Record<string, string>>({})
const loading = ref(false)
const error = ref('')
const postingId = ref('')
const pagination = ref({ page: 1, pageSize: 20, total: 0, totalPages: 1 })
const currentPage = ref(1)

let refreshTimer: ReturnType<typeof setInterval> | null = null
const milestones = computed(() => isZh.value ? ['\u521b\u5efa', '\u62e3\u914d', '\u5df2\u62e3', '\u53d1\u8d27\u8fc7\u8d26'] : ['Created', 'Picking', 'Picked', 'PGI'])

// Status mapping
const STATUS_LABEL_ZH: Record<string, string> = {
  OPEN: '\u521b\u5efa\u4e2d',
  PICKING: '\u62e3\u914d\u4e2d',
  SHIPPED: '\u5df2\u62e3\u914d',
  IN_TRANSIT: '\u8fd0\u8f93\u4e2d',
  PGI_DONE: '\u5df2\u5b8c\u6210',
  CANCELLED: '\u5df2\u53d6\u6d88',
}
const STATUS_LABEL_EN: Record<string, string> = {
  OPEN: 'Creating',
  PICKING: 'Picking',
  SHIPPED: 'Picked',
  IN_TRANSIT: 'In Transit',
  PGI_DONE: 'Completed',
  CANCELLED: 'Cancelled',
}
function statusLabel(status: string) {
  return (isZh.value ? STATUS_LABEL_ZH : STATUS_LABEL_EN)[status] || status
}

const STATUS_INDEX: Record<string, number> = {
  CANCELLED: -1,
  OPEN: 0,
  PICKING: 1,
  SHIPPED: 2,
  IN_TRANSIT: 2,
  PGI_DONE: 3,
}

function mapRow(item: DeliveryListItem) {
  const st = statusLabel(item.deliveryStatus)
  const si = STATUS_INDEX[item.deliveryStatus] ?? 0
  const actionMap = isZh.value
    ? { OPEN: '\u5f00\u59cb\u62e3\u914d', PICKING: '\u62e3\u914d', SHIPPED: '\u53d1\u8d27', IN_TRANSIT: '\u53d1\u8d27\u8fc7\u8d26' } as Record<string, string>
    : { OPEN: 'Start Picking', PICKING: 'Pick Items', SHIPPED: 'Ship', IN_TRANSIT: 'Post GI' } as Record<string, string>
  const total = item.totalQuantity ?? 0
  const delivered = item.deliveredQuantity ?? 0

  return {
    id: item.deliveryId,
    dn: item.deliveryId,
    sn: item.salesOrderId || 'N/A',
    cn: item.shipToPartyName || item.shipToParty || 'N/A',
    dd: item.plannedDeliveryDate || 'N/A',
    gi: item.plannedGiDate || 'N/A',
    st,
    si,
    dt: `${Number(delivered).toFixed(0)} / ${Number(total).toFixed(0)}`,
    rawStatus: item.deliveryStatus,
    actionLabel: actionMap[item.deliveryStatus] || '',
  }
}

const displayedRows = computed(() => rawItems.value.map(mapRow))

function sc(s: string) {
  const m: Record<string, string> = {
    Completed: 's-done',
    Picked: 's-ship',
    Picking: 's-pick',
    Creating: 's-creating',
    'In Transit': 's-pick',
    Cancelled: 's-cancel',
  }
  return m[s] || ''
}

async function loadPartners() {
  try {
    const res = await fetchPartners({ limit: 999 })
    const items: Partner[] = res.items || []
    partnerMap.value = items.reduce((acc: Record<string, string>, p: Partner) => {
      if (p.bpId) acc[p.bpId] = p.bpName
      return acc
    }, {})
  } catch (e) { /* partner names already served by backend; fallback only */ }
}

async function loadDeliveries() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchDeliveries({
      page: currentPage.value,
      pageSize: 20,
      deliveryNo: f.dn || undefined,
      salesOrderNo: f.sn || undefined,
      customerName: f.cn || undefined,
      status: f.st || undefined,
    })
    rawItems.value = res.items || []
    pagination.value = res.pagination || { page: 1, pageSize: 20, total: 0, totalPages: 1 }
  } catch (err: any) {
    error.value = err?.message || 'Failed to load deliveries'
    console.error('Fetch status failed:', err)
  } finally {
    loading.value = false
  }
}

function startRefreshTimer() {
  if (refreshTimer) clearInterval(refreshTimer)
  if (!ar.value) return
  const ms = ri.value === '30s' ? 30000 : ri.value === '60s' ? 60000 : 300000
  refreshTimer = setInterval(() => loadDeliveries(), ms)
}

function search() {
  currentPage.value = 1
  loadDeliveries()
}

function reset() {
  Object.assign(f, { dn: '', sn: '', cn: '', st: '' })
  currentPage.value = 1
  loadDeliveries()
}

async function processDelivery(row: any) {
  if (row.rawStatus === 'PICKING') {
    router.push('/delivery/detail/' + row.id)
    return
  }
  if (postingId.value) return
  if (!(await confirm(`${row.actionLabel} for delivery ${row.dn}?`))) return
  postingId.value = row.id
  try {
    if (row.rawStatus === 'OPEN') await startPicking(row.id)
    else if (row.rawStatus === 'SHIPPED') await shipDelivery(row.id)
    else if (row.rawStatus === 'IN_TRANSIT') await postGoodsIssue(row.id)
    alert(`${row.actionLabel} completed`)
    loadDeliveries()
  } catch (err: any) {
    alert(`${row.actionLabel} failed: ` + (err?.message || 'Unknown error'))
  } finally {
    postingId.value = ''
  }
}

function goPage(p: number) {
  if (p < 1 || p > pagination.value.totalPages) return
  currentPage.value = p
  loadDeliveries()
}

onMounted(async () => {
  await Promise.all([loadPartners(), loadDeliveries()])
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})

watch([ar, ri], startRefreshTimer)
</script>

<style scoped>
.page{padding:28px 36px;max-width:1340px;margin:0 auto;}
.header-card{display:flex;align-items:center;justify-content:space-between;background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:16px;padding:20px 24px;border:1px solid rgba(173,188,159,0.18);box-shadow:0 2px 8px rgba(173,188,159,0.12);margin-bottom:20px;}
.hc-left{display:flex;align-items:center;gap:14px;}
.hc-icon{width:44px;height:44px;border-radius:12px;background:rgba(67,104,80,0.08);display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.hc-title{font-size:18px;font-weight:800;color:#12372A;margin:0;}
.hc-sub{font-size:12px;color:rgba(18,55,42,0.45);margin:2px 0 0;}
.hc-right{display:flex;align-items:center;gap:12px;}
.auto-refresh{font-size:12px;color:rgba(18,55,42,0.5);display:flex;align-items:center;gap:6px;cursor:pointer;}
.form-select-sm{height:32px;padding:0 8px;font-size:11px;}

.filter-bar{display:flex;gap:10px;margin-bottom:16px;align-items:center;flex-wrap:wrap;}
.form-input,.form-select{height:38px;border:1px solid rgba(173,188,159,0.4);border-radius:8px;padding:0 12px;font-size:13px;color:#12372A;background:rgba(251,250,218,0.35);font-family:inherit;outline:none;min-width:130px;transition:all 0.2s;}
.form-input:focus,.form-select:focus{border-color:#436850;box-shadow:0 0 0 3px rgba(67,104,80,0.06);background:#fff;}

.error-msg {
  color: #D9534F;
  font-size: 13px;
  padding: 10px 14px;
  background: rgba(217, 83, 79, 0.08);
  border-radius: 8px;
  margin-bottom: 14px;
}

.data-card{background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:14px;border:1px solid rgba(173,188,159,0.15);box-shadow:0 2px 6px rgba(173,188,159,0.1);overflow:hidden;}
.table-scroll{overflow-x:auto;}
.data-table{width:100%;border-collapse:collapse;font-size:13px;min-width:1250px;}
.data-table th{text-align:left;padding:12px 14px;font-size:10px;font-weight:700;color:rgba(18,55,42,0.45);text-transform:uppercase;letter-spacing:0.8px;background:rgba(173,188,159,0.08);border-bottom:1px solid rgba(173,188,159,0.2);white-space:nowrap;}
.data-table th.num{text-align:right;}
.data-table td{padding:11px 14px;border-bottom:1px solid rgba(173,188,159,0.08);color:#12372A;white-space:nowrap;}
.data-table td.num{text-align:right;}
.qty-cell{min-width:140px; padding-left: 20px !important; padding-right: 20px !important; color: #436850; font-weight: 700; text-align: right; border-left: 1px solid rgba(173,188,159,0.15);}
.data-row:hover{background:rgba(67,104,80,0.025);}
.empty-cell{text-align:center;padding:40px;color:rgba(18,55,42,0.4);}
.mono{font-family:'SF Mono',Consolas,monospace;font-size:12px;}
.sticky-left{position:sticky;left:0;background:#fdfce8;z-index:10;box-shadow:2px 0 4px rgba(18,55,42,0.02);}
.data-row:hover .sticky-left{background:#f7f5d1;}
.data-table th.sticky-left{background:rgba(173,188,159,0.1) !important; z-index:11;}

.stag{font-size:11px;font-weight:600;padding:4px 10px;border-radius:6px;display:inline-block;white-space:nowrap;}
.s-done{background:rgba(67,104,80,0.1);color:#436850;}
.s-ship{background:rgba(67,104,80,0.08);color:#2d4a38;}
.s-pick{background:rgba(173,188,159,0.2);color:#436850;}
.s-creating{background:rgba(240,173,78,0.12);color:#c98a20;}
.s-cancel{background:rgba(217,83,79,0.1);color:#D9534F;}

.prog-hdr{min-width:320px;padding-left:24px !important;padding-right:24px !important;}
.qty-hdr{min-width:140px; text-align: right !important; border-left: 1px solid rgba(173,188,159,0.15);}
.ms-bar{display:flex;align-items:center;gap:0;padding:4px 0 24px;width:100%;}
.ms-step{display:flex;flex-direction:column;align-items:center;position:relative;flex:1;min-width:50px;}
.ms-dot{width:8px;height:8px;border-radius:50%;border:2px solid rgba(173,188,159,0.35);background:#FBFADA;z-index:2;}
.ms-dot.done{background:#436850;border-color:#436850;}
.ms-dot.cur{background:#436850;border-color:#436850;box-shadow:0 0 0 3px rgba(67,104,80,0.15);}
.ms-line{position:absolute;top:3.5px;left:50%;width:100%;height:2px;background:rgba(173,188,159,0.25);z-index:1;}
.ms-line.done{background:#436850;}
.ms-lbl{font-size:8px;color:rgba(18,55,42,0.4);margin-top:2px;white-space:nowrap;position:absolute;top:100%;transform: translateY(4px);}
.row-actions{display:flex;align-items:center;justify-content:flex-start;gap:12px;min-width:180px;padding-left:10px;border-left: 1px solid rgba(173,188,159,0.15);}
.link{color:#436850;cursor:pointer;font-weight:600;font-size:12px;white-space:nowrap;}
.link:hover{text-decoration:underline;}
.link.disabled{color:rgba(18,55,42,0.3);cursor:not-allowed;text-decoration:none;}


.table-footer{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-top:1px solid rgba(173,188,159,0.15);}
.tf-left{display:flex;align-items:center;gap:10px;}
.tf-total{font-size:12px;color:rgba(18,55,42,0.4);}
.tf-right{display:flex;align-items:center;gap:8px;}
.tf-label{font-size:11px;color:rgba(18,55,42,0.35);}
.pg-input{width:50px;height:30px;border:1px solid rgba(173,188,159,0.35);border-radius:6px;text-align:center;font-size:12px;outline:none;}
.pager{display:flex;gap:4px;}
.pg-btn{min-width:30px;height:30px;border:1px solid rgba(173,188,159,0.25);border-radius:6px;background:rgba(251,250,218,0.3);font-size:12px;color:#12372A;cursor:pointer;display:flex;align-items:center;justify-content:center;}
.pg-btn.active{background:#436850;color:#FBFADA;border-color:#436850;}

.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 20px;font-size:13px;font-weight:600;border-radius:8px;cursor:pointer;transition:all 0.2s;font-family:inherit;}
.btn-primary{background:linear-gradient(135deg,#436850,#365440);color:#FBFADA;border:none;box-shadow:0 2px 8px rgba(67,104,80,0.25);}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(67,104,80,0.3);}
.btn-primary:disabled{opacity:0.6;cursor:not-allowed;transform:none;}
.btn-outline{background:none;color:rgba(18,55,42,0.5);border:1px solid rgba(173,188,159,0.35);}
.btn-outline:hover{border-color:rgba(18,55,42,0.3);color:#12372A;}
.btn-outline:disabled{opacity:0.6;cursor:not-allowed;}
</style>
