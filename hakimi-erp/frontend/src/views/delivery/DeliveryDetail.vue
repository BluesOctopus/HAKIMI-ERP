<template>
  <MainLayout>
    <div class="page" v-if="loading">
      <div class="section-card" style="padding:40px;text-align:center;color:rgba(18,55,42,0.4)">
        Loading delivery details...
      </div>
    </div>
    <div class="page" v-else-if="error">
      <div class="error-msg">{{ error }}</div>
      <button class="btn btn-outline" @click="load">Retry</button>
    </div>
    <div class="page" v-else-if="delivery">
      <div class="top-bar">
        <button class="back-btn" @click="$router.push('/delivery/monitor')"><svg viewBox="0 0 20 20" width="16" height="16"><path d="M12 4l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>Back</button>
        <div class="hc-icon"><svg viewBox="0 0 24 24" width="22" height="22"><rect x="2" y="5" width="20" height="13" rx="2" fill="none" stroke="#436850" stroke-width="1.8"/><path d="M6 5V3M18 5V3M2 11h20M7 16h3" fill="none" stroke="#436850" stroke-width="1.5" stroke-linecap="round"/></svg></div>
        <div class="top-info">
          <span class="ti-label">Delivery No.</span>
          <span class="ti-value">{{ delivery.delivery_id }}</span>
          <span class="ti-sub">Sales Order {{ delivery.sales_order_id || 'N/A' }} &middot; {{ customerName }}</span>
        </div>
        <div style="margin-left:auto;display:flex;align-items:center;gap:10px;">
          <span class="stag" :class="statusClass">{{ statusLabel }}</span>
          <button class="btn btn-primary" @click="postPgi" :disabled="posting || !canPgi">
            <svg viewBox="0 0 20 20" width="14" height="14"><path d="M10 3v10M6 9l4 4 4-4M3 17h14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            {{ posting ? 'Posting...' : (canPgi ? 'Post GI' : 'GI Done') }}
          </button>
          <button class="btn btn-outline" @click="print"><svg viewBox="0 0 20 20" width="14" height="14"><rect x="3" y="4" width="14" height="10" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 8h8M6 11h5" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>Print</button>
        </div>
      </div>

      <div class="info-cards">
        <div class="ic"><span class="ic-label">Delivery Date</span><span class="ic-value">{{ delivery.planned_delivery_date || 'N/A' }}</span></div>
        <div class="ic"><span class="ic-label">Planned GI Date</span><span class="ic-value">{{ delivery.planned_gi_date || 'N/A' }}</span></div>
        <div class="ic"><span class="ic-label">Shipping Point</span><span class="ic-value">{{ delivery.shipping_point || 'N/A' }}</span></div>
        <div class="ic"><span class="ic-label">Delivered / Total</span><span class="ic-value mono">{{ deliveredQty }} / {{ totalQty }}</span></div>
      </div>

      <div class="section-card">
        <h3 class="sc-title">Delivery Progress</h3>
        <p class="sc-hint">Current milestone reflects the latest backend status.</p>
        <div class="timeline">
          <div v-for="(s,i) in steps" :key="i" class="tl-step" :class="{done:s.done,cur:s.cur}">
            <div class="tl-dot"></div><div v-if="i<3" class="tl-line"></div>
            <div class="tl-info"><span class="tl-status">{{ s.label }}</span><span class="tl-time">{{ s.time }}</span></div>
          </div>
        </div>
      </div>

      <div class="two-col">
        <div class="section-card">
          <h3 class="sc-title">Shipment Information</h3>
          <div class="si-grid">
            <div class="si-item"><span class="si-label">Ship-to Party</span><span class="si-value">{{ customerName }}</span></div>
            <div class="si-item"><span class="si-label">Ship-to Address</span><span class="si-value mono">{{ shipToAddress }}</span></div>
            <div class="si-item"><span class="si-label">Shipping Point</span><span class="si-value">{{ delivery.shipping_point || 'N/A' }}</span></div>
            <div class="si-item"><span class="si-label">Route</span><span class="si-value">Warehouse → Customer Site</span></div>
            <div class="si-item"><span class="si-label">Carrier / Driver</span><span class="si-value">GreenLine Freight · Daniel Wu</span></div>
            <div class="si-item"><span class="si-label">Latest GPS</span><span class="si-value">In transit <span class="gps-time">Updated recently</span></span></div>
          </div>
        </div>
        <div class="section-card">
          <h3 class="sc-title">Order Items</h3>
          <table class="data-table">
            <thead><tr><th>Material</th><th>Description</th><th class="num">Qty</th><th>Status</th></tr></thead>
            <tbody>
              <tr v-for="item in delivery.items" :key="item.delivery_item_id">
                <td class="mono">{{ item.material_id }}</td>
                <td>{{ materialName(item.material_id) }}</td>
                <td class="num mono">{{ Number(item.delivery_quantity || 0).toLocaleString() }}</td>
                <td><span class="stag" :class="itemStatusClass(item)">{{ itemStatus(item) }}</span></td>
              </tr>
              <tr v-if="!delivery.items || delivery.items.length === 0"><td colspan="4" style="text-align:center;padding:20px;color:#999">No items.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <SuccessModal
      v-model:visible="successVisible"
      title="Goods Issue Posted"
      :message="successMsg"
      @confirm="onSuccessConfirm"
    />
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainLayout from '@/layout/MainLayout.vue'
import SuccessModal from '@/components/SuccessModal.vue'
import { fetchDeliveryById, postGoodsIssue, fetchPartners, fetchMaterials } from '@/api'
import type { Delivery } from '@/api/modules/logistics'
import type { Partner, Material } from '@/api/modules/master'

const route = useRoute()
const router = useRouter()
const deliveryId = computed(() => route.params.id as string)

const delivery = ref<Delivery | null>(null)
const partnerMap = ref<Record<string, Partner>>({})
const materialMap = ref<Record<string, Material>>({})
const loading = ref(false)
const error = ref('')
const posting = ref(false)
const successVisible = ref(false)
const successMsg = ref('')

const customer = computed(() => delivery.value ? partnerMap.value[delivery.value.ship_to_party] : null)
const customerName = computed(() => customer.value?.bp_name || delivery.value?.ship_to_party || 'Unknown')
const shipToAddress = computed(() => {
  const p = customer.value
  if (!p) return 'N/A'
  const parts = [p.street, p.city, p.country, p.postal_code].filter(Boolean)
  return parts.join(', ') || 'N/A'
})

const totalQty = computed(() => {
  if (!delivery.value?.items) return 0
  return delivery.value.items.reduce((acc, it) => acc + (Number(it.delivery_quantity) || 0), 0)
})
const deliveredQty = computed(() => {
  const status = delivery.value?.delivery_status
  return status === 'PGI_DONE' || status === 'CANCELLED' ? totalQty.value : 0
})

const statusLabel = computed(() => {
  const s = delivery.value?.delivery_status
  if (s === 'PGI_DONE') return 'Completed'
  if (s === 'CANCELLED') return 'Cancelled'
  return delivery.value?.picking_date ? 'Picking' : 'Creating'
})
const statusClass = computed(() => {
  switch (statusLabel.value) {
    case 'Completed': return 's-done'
    case 'Picking': return 's-pick'
    case 'Cancelled': return 's-cancel'
    default: return 's-creating'
  }
})
const canPgi = computed(() => delivery.value?.delivery_status === 'OPEN')

const steps = computed(() => {
  const d = delivery.value
  if (!d) return []
  const created = !!d.created_time
  const picked = !!d.picking_date
  const shipped = d.delivery_status === 'PGI_DONE' || !!d.actual_gi_date
  const completed = d.delivery_status === 'PGI_DONE'
  const list = [
    { label: 'Created', done: created, time: d.created_time ? formatDate(d.created_time) : 'Pending' },
    { label: 'Picked', done: picked, time: d.picking_date ? formatDate(d.picking_date) : 'Pending' },
    { label: 'Shipped', done: shipped, time: d.actual_gi_date ? formatDate(d.actual_gi_date) : 'Pending' },
    { label: 'Completed', done: completed, time: completed ? 'Done' : 'Pending' }
  ]
  let cur = -1
  for (let i = 0; i < list.length; i++) {
    if (!list[i].done) { cur = i; break }
  }
  return list.map((s, i) => ({ ...s, cur: i === cur }))
})

function formatDate(v: string | Date) {
  if (!v) return 'N/A'
  const d = new Date(v)
  return isNaN(d.getTime()) ? String(v) : d.toLocaleString('en-US', { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function materialName(id: string) {
  return materialMap.value[id]?.material_name || id
}

function itemStatus(item: any) {
  if (delivery.value?.delivery_status === 'CANCELLED') return 'Cancelled'
  if (delivery.value?.delivery_status === 'PGI_DONE') return 'Shipped'
  return 'Open'
}
function itemStatusClass(item: any) {
  const s = itemStatus(item)
  return s === 'Shipped' ? 's-done' : s === 'Cancelled' ? 's-cancel' : 's-pick'
}

async function load() {
  if (!deliveryId.value) {
    error.value = 'Missing delivery ID'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const [delRes, partRes, matRes] = await Promise.all([
      fetchDeliveryById(deliveryId.value),
      fetchPartners({ page_size: 100 }),
      fetchMaterials({ page_size: 100 })
    ])
    delivery.value = delRes
    partnerMap.value = (partRes.items || []).reduce((acc: Record<string, Partner>, p: Partner) => {
      if (p.bp_id) acc[p.bp_id] = p
      return acc
    }, {})
    materialMap.value = (matRes.items || []).reduce((acc: Record<string, Material>, m: Material) => {
      if (m.material_id) acc[m.material_id] = m
      return acc
    }, {})
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err.message || 'Failed to load delivery details'
    console.error('Fetch delivery detail failed:', err)
  } finally {
    loading.value = false
  }
}

async function postPgi() {
  if (!delivery.value || !canPgi.value) return
  if (!confirm(`Post Goods Issue for delivery ${delivery.value.delivery_id}?`)) return
  posting.value = true
  try {
    await postGoodsIssue(delivery.value.delivery_id)
    successMsg.value = `Goods Issue posted successfully for delivery ${delivery.value.delivery_id}.`
    successVisible.value = true
    load()
  } catch (err: any) {
    alert('Post GI failed: ' + (err?.response?.data?.detail || err?.response?.data?.message || err.message))
  } finally {
    posting.value = false
  }
}

function onSuccessConfirm() {
  load()
}

function print() {
  window.print()
}

onMounted(() => load())
</script>

<style scoped>
.page{padding:28px 36px;max-width:1200px;margin:0 auto;}
.top-bar{display:flex;align-items:center;gap:16px;margin-bottom:22px;flex-wrap:wrap;}
.back-btn{display:inline-flex;align-items:center;gap:6px;background:none;border:1px solid rgba(173,188,159,0.35);border-radius:8px;padding:8px 16px;font-size:13px;color:rgba(18,55,42,0.55);cursor:pointer;font-family:inherit;transition:all 0.2s;}
.back-btn:hover{border-color:#436850;color:#436850;}
.hc-icon{width:42px;height:42px;border-radius:10px;background:rgba(67,104,80,0.08);display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.top-info{display:flex;flex-direction:column;}
.ti-label{font-size:10px;color:rgba(18,55,42,0.35);text-transform:uppercase;letter-spacing:1px;font-weight:600;}
.ti-value{font-size:22px;font-weight:800;color:#12372A;font-family:'SF Mono',Consolas,monospace;}
.ti-sub{font-size:12px;color:rgba(18,55,42,0.4);}
.stag{font-size:11px;font-weight:600;padding:5px 12px;border-radius:6px;}
.s-done{background:rgba(67,104,80,0.1);color:#436850;}
.s-pick{background:rgba(240,173,78,0.12);color:#c98a20;}
.s-creating{background:rgba(173,188,159,0.2);color:#436850;}
.s-cancel{background:rgba(217,83,79,0.1);color:#D9534F;}

.info-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;}
.ic{background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:12px;padding:16px 18px;border:1px solid rgba(173,188,159,0.15);box-shadow:0 2px 6px rgba(173,188,159,0.1);}
.ic-label{font-size:10px;color:rgba(18,55,42,0.4);font-weight:600;text-transform:uppercase;letter-spacing:0.5px;display:block;margin-bottom:6px;}
.ic-value{font-size:15px;font-weight:700;color:#12372A;}

.section-card{background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:14px;padding:22px;border:1px solid rgba(173,188,159,0.15);box-shadow:0 2px 6px rgba(173,188,159,0.1);margin-bottom:18px;}
.sc-title{font-size:14px;font-weight:700;color:#436850;margin:0 0 12px;display:flex;align-items:center;gap:8px;}
.sc-title::before{content:'';width:3px;height:13px;background:#436850;border-radius:2px;}
.sc-hint{font-size:12px;color:rgba(18,55,42,0.4);margin:0 0 18px;font-style:italic;}

.timeline{display:flex;align-items:flex-start;padding:8px 0;}
.tl-step{flex:1;position:relative;display:flex;flex-direction:column;align-items:center;}
.tl-dot{width:13px;height:13px;border-radius:50%;border:2px solid rgba(173,188,159,0.35);background:#FBFADA;z-index:1;}
.tl-step.done .tl-dot{background:#436850;border-color:#436850;}
.tl-step.cur .tl-dot{background:#436850;border-color:#436850;box-shadow:0 0 0 4px rgba(67,104,80,0.12);}
.tl-line{position:absolute;top:6px;left:50%;width:100%;height:2px;background:rgba(173,188,159,0.25);}
.tl-step.done .tl-line{background:#436850;}
.tl-info{margin-top:10px;text-align:center;}
.tl-status{font-size:11px;font-weight:600;color:rgba(18,55,42,0.45);display:block;}
.tl-step.cur .tl-status,.tl-step.done .tl-status{color:#436850;}
.tl-time{font-size:10px;color:rgba(18,55,42,0.28);display:block;margin-top:2px;}

.two-col{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
.si-grid{display:flex;flex-direction:column;gap:14px;}
.si-item{display:flex;flex-direction:column;gap:2px;}
.si-label{font-size:10px;color:rgba(18,55,42,0.38);font-weight:600;text-transform:uppercase;letter-spacing:0.5px;}
.si-value{font-size:13px;color:#12372A;line-height:1.6;}
.gps-time{font-size:10px;color:rgba(18,55,42,0.25);}

.data-table{width:100%;border-collapse:collapse;font-size:13px;}
.data-table th{text-align:left;padding:9px 12px;font-size:10px;font-weight:700;color:rgba(18,55,42,0.4);text-transform:uppercase;letter-spacing:0.5px;border-bottom:1px solid rgba(173,188,159,0.2);}
.data-table th.num{text-align:right;}
.data-table td{padding:9px 12px;border-bottom:1px solid rgba(173,188,159,0.07);color:#12372A;}
.data-table td.num{text-align:right;}
.mono{font-family:'SF Mono',Consolas,monospace;font-size:12px;}

.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 18px;font-size:13px;font-weight:600;border-radius:8px;cursor:pointer;transition:all 0.2s;font-family:inherit;}
.btn-primary{background:linear-gradient(135deg,#436850,#365440);color:#FBFADA;border:none;box-shadow:0 2px 8px rgba(67,104,80,0.25);}
.btn-primary:hover{transform:translateY(-1px);}
.btn-primary:disabled{opacity:0.6;cursor:not-allowed;transform:none;}
.btn-outline{background:none;color:rgba(18,55,42,0.5);border:1px solid rgba(173,188,159,0.35);}
.btn-outline:hover{border-color:#436850;color:#436850;}
.error-msg {
  color: #D9534F;
  font-size: 13px;
  padding: 10px 14px;
  background: rgba(217, 83, 79, 0.08);
  border-radius: 8px;
  margin-bottom: 14px;
}
</style>
