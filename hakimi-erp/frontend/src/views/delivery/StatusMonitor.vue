<template>
  <MainLayout>
    <div class="page">
      <div class="header-card">
        <div class="hc-left">
          <div class="hc-icon"><svg viewBox="0 0 24 24" width="22" height="22"><rect x="2" y="5" width="20" height="13" rx="2" fill="none" stroke="#436850" stroke-width="1.8"/><path d="M6 5V3M18 5V3M2 11h20M7 16h3" fill="none" stroke="#436850" stroke-width="1.5" stroke-linecap="round"/></svg></div>
          <div class="hc-text"><h2 class="hc-title">Delivery Status Monitoring</h2><p class="hc-sub">Monitor delivery progress in real time. The status of each order is clear at a glance.</p></div>
        </div>
        <div class="hc-right">
          <label class="auto-refresh"><input type="checkbox" v-model="ar" /> Auto Refresh</label>
          <select class="form-select form-select-sm" v-model="ri"><option>30s</option><option>60s</option><option>5min</option></select>
        </div>
      </div>

      <div class="filter-bar">
        <input type="text" class="form-input" v-model="f.dn" placeholder="Delivery No." />
        <input type="text" class="form-input" v-model="f.sn" placeholder="Sales Order No." />
        <input type="text" class="form-input" v-model="f.cn" placeholder="Customer Name" />
        <select class="form-select" v-model="f.st"><option value="">All Statuses</option><option>Creating</option><option>Picking</option><option>Shipped</option><option>Completed</option><option>Cancelled</option></select>
        <button class="btn btn-primary" @click="search" :disabled="loading">Search</button>
        <button class="btn btn-outline" @click="reset" :disabled="loading">Reset</button>
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <div class="data-card">
        <div class="table-scroll"><table class="data-table">
          <thead><tr>
            <th class="sticky-left">Delivery No.</th><th>Sales Order No.</th><th>Customer Name</th><th>Delivery Date</th><th>Planned GI Date</th><th>Status</th>
            <th class="prog-hdr">Progress</th><th class="num">Delivered / Total</th><th class="sticky-right">Action</th>
          </tr></thead>
          <tbody>
            <tr v-if="loading && displayedRows.length === 0"><td colspan="9" class="empty-cell">Loading deliveries...</td></tr>
            <tr v-for="row in displayedRows" :key="row.id" class="data-row">
              <td class="sticky-left mono">{{ row.dn }}</td><td class="mono">{{ row.sn }}</td><td>{{ row.cn }}</td><td>{{ row.dd }}</td><td>{{ row.gi }}</td>
              <td><span class="stag" :class="sc(row.st)">{{ row.st }}</span></td>
              <td class="prog-hdr"><div class="ms-bar">
                <div v-for="(m,i) in milestones" :key="i" class="ms-step">
                  <div class="ms-dot" :class="{done:row.si>=i,cur:row.si===i}"></div>
                  <div v-if="i<3" class="ms-line" :class="{done:row.si>i}"></div>
                  <span class="ms-lbl">{{ m }}</span>
                </div>
              </div></td>
              <td class="num mono">{{ row.dt }}</td>
              <td class="sticky-right">
                <a class="link" @click="$router.push('/delivery/detail/'+row.id)">View Details</a>
                <a v-if="row.canPgi" class="link pgi-link" :class="{disabled: postingId === row.id}" @click="postPgi(row)">
                  {{ postingId === row.id ? 'Posting...' : 'Post GI' }}
                </a>
              </td>
            </tr>
            <tr v-if="!loading && displayedRows.length === 0"><td colspan="9" class="empty-cell">No deliveries found.</td></tr>
          </tbody>
        </table></div>
        <div class="table-footer">
          <div class="tf-left"><span class="tf-total">Total {{ displayedRows.length }} items</span><select class="form-select form-select-sm" style="width:80px"><option>10 / page</option><option>20</option><option>50</option></select></div>
          <div class="pager"><button class="pg-btn active">1</button><button class="pg-btn">2</button><button class="pg-btn">3</button></div>
          <div class="tf-right"><span class="tf-label">Go to</span><input type="text" class="pg-input" placeholder="page" /></div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import MainLayout from '@/layout/MainLayout.vue'
import { fetchDeliveries, postGoodsIssue, fetchPartners } from '@/api'
import type { Delivery } from '@/api/modules/logistics'
import type { Partner } from '@/api/modules/master'

const ar = ref(true)
const ri = ref('30s')
const f = reactive({ dn: '', sn: '', cn: '', st: '' })

const rawDeliveries = ref<Delivery[]>([])
const partnerMap = ref<Record<string, Partner>>({})
const loading = ref(false)
const error = ref('')
const postingId = ref('')

let refreshTimer: ReturnType<typeof setInterval> | null = null
const milestones = ['Created', 'Picked', 'Shipped', 'Completed']

function computeStatus(i: any) {
  const status = i.delivery_status
  if (status === 'CANCELLED') return { st: 'Cancelled', si: -1, canPgi: false }
  if (status === 'PGI_DONE') {
    if (i.actual_gi_date) return { st: 'Completed', si: 3, canPgi: false }
    return { st: 'Shipped', si: 2, canPgi: false }
  }
  if (i.picking_date) return { st: 'Picking', si: 1, canPgi: true }
  return { st: 'Creating', si: 0, canPgi: true }
}

const allRows = computed(() => {
  return rawDeliveries.value.map((i: any) => {
    const { st, si, canPgi } = computeStatus(i)
    const total = (i.items || []).reduce((acc: number, it: any) => acc + (parseFloat(it.delivery_quantity) || 0), 0)
    const delivered = st === 'Completed' || st === 'Shipped' ? total : 0
    return {
      id: i.delivery_id,
      dn: i.delivery_id,
      sn: i.sales_order_id || 'N/A',
      cn: partnerMap.value[i.ship_to_party]?.bp_name || i.ship_to_party || 'Unknown',
      dd: i.planned_delivery_date || 'N/A',
      gi: i.planned_gi_date || 'N/A',
      st,
      si,
      dt: `${delivered} / ${total}`,
      canPgi,
      deliveryId: i.delivery_id
    }
  })
})

const displayedRows = computed(() => {
  return allRows.value.filter(r => {
    if (f.dn && !r.dn.toLowerCase().includes(f.dn.toLowerCase())) return false
    if (f.sn && !r.sn.toLowerCase().includes(f.sn.toLowerCase())) return false
    if (f.cn && !r.cn.toLowerCase().includes(f.cn.toLowerCase())) return false
    if (f.st && r.st !== f.st) return false
    return true
  })
})

function sc(s: string) {
  const m: Record<string, string> = {
    'Completed': 's-done',
    'Shipped': 's-ship',
    'Picking': 's-pick',
    'Creating': 's-creating',
    'Cancelled': 's-cancel'
  }
  return m[s] || ''
}

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    const [delRes, partRes] = await Promise.all([
      fetchDeliveries({ page_size: 100 }),
      fetchPartners({ page_size: 100 })
    ])
    rawDeliveries.value = delRes.items || []
    const partners = partRes.items || []
    partnerMap.value = partners.reduce((acc: Record<string, Partner>, p: Partner) => {
      if (p.bp_id) acc[p.bp_id] = p
      return acc
    }, {})
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err.message || 'Failed to load deliveries'
    console.error('Fetch status failed:', err)
  } finally {
    loading.value = false
  }
}

function startRefreshTimer() {
  if (refreshTimer) clearInterval(refreshTimer)
  if (!ar.value) return
  const ms = ri.value === '30s' ? 30000 : ri.value === '60s' ? 60000 : 300000
  refreshTimer = setInterval(() => fetchData(), ms)
}

function search() { fetchData() }
function reset() {
  Object.assign(f, { dn: '', sn: '', cn: '', st: '' })
  fetchData()
}

async function postPgi(row: any) {
  if (postingId.value) return
  if (!confirm(`Post Goods Issue for delivery ${row.dn}?`)) return
  postingId.value = row.id
  try {
    await postGoodsIssue(row.deliveryId)
    alert('Goods Issue posted successfully')
    fetchData()
  } catch (err: any) {
    alert('Post GI failed: ' + (err?.response?.data?.detail || err?.response?.data?.message || err.message))
  } finally {
    postingId.value = ''
  }
}

onMounted(() => {
  fetchData()
  startRefreshTimer()
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
.data-table{width:100%;border-collapse:collapse;font-size:13px;min-width:1000px;}
.data-table th{text-align:left;padding:12px 14px;font-size:10px;font-weight:700;color:rgba(18,55,42,0.45);text-transform:uppercase;letter-spacing:0.8px;background:rgba(173,188,159,0.08);border-bottom:1px solid rgba(173,188,159,0.2);white-space:nowrap;}
.data-table th.num{text-align:right;}
.data-table td{padding:11px 14px;border-bottom:1px solid rgba(173,188,159,0.08);color:#12372A;white-space:nowrap;}
.data-table td.num{text-align:right;}
.data-row:hover{background:rgba(67,104,80,0.025);}
.empty-cell{text-align:center;padding:40px;color:rgba(18,55,42,0.4);}
.mono{font-family:'SF Mono',Consolas,monospace;font-size:12px;}
.sticky-left{position:sticky;left:0;background:inherit;z-index:1;box-shadow:2px 0 4px rgba(18,55,42,0.03);}
.sticky-right{position:sticky;right:0;background:inherit;z-index:1;box-shadow:-2px 0 4px rgba(18,55,42,0.03);}

.stag{font-size:11px;font-weight:600;padding:4px 10px;border-radius:6px;}
.s-done{background:rgba(67,104,80,0.1);color:#436850;}
.s-ship{background:rgba(67,104,80,0.08);color:#2d4a38;}
.s-pick{background:rgba(173,188,159,0.2);color:#436850;}
.s-creating{background:rgba(240,173,78,0.12);color:#c98a20;}
.s-cancel{background:rgba(217,83,79,0.1);color:#D9534F;}

.prog-hdr{min-width:260px;}
.ms-bar{display:flex;align-items:center;gap:0;padding-top:2px;}
.ms-step{display:flex;flex-direction:column;align-items:center;position:relative;min-width:58px;}
.ms-dot{width:10px;height:10px;border-radius:50%;border:2px solid rgba(173,188,159,0.35);background:#FBFADA;}
.ms-dot.done{background:#436850;border-color:#436850;}
.ms-dot.cur{background:#436850;border-color:#436850;box-shadow:0 0 0 3px rgba(67,104,80,0.15);}
.ms-line{position:absolute;top:5px;left:50%;width:100%;height:2px;background:rgba(173,188,159,0.25);}
.ms-line.done{background:#436850;}
.ms-lbl{font-size:9px;color:rgba(18,55,42,0.3);margin-top:3px;white-space:nowrap;}
.link{color:#436850;cursor:pointer;font-weight:600;font-size:12px;margin-left:10px;}
.link:first-child{margin-left:0;}
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
