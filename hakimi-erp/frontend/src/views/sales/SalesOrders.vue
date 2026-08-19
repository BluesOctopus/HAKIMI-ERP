<template>
  <div class="page">
    <div class="header-card">
      <div class="hc-left">
        <div class="hc-icon">
          <svg viewBox="0 0 24 24" width="22" height="22">
            <path d="M4 4h3l1 5h7l2-5h2M7 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm7 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4z" fill="none" stroke="#436850" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="hc-text">
          <h2 class="hc-title">{{ isZh ? '\u9500\u552e\u8ba2\u5355' : 'Sales Orders' }}</h2>
          <p class="hc-sub">{{ isZh ? '\u7ba1\u7406\u5e76\u8ddf\u8e2a\u4f01\u4e1a\u5185\u7684\u6240\u6709\u9500\u552e\u8ba2\u5355\u3002' : 'Manage and track all sales orders across the organization.' }}</p>
        </div>
      </div>
      <div class="hc-right">
        <button class="btn btn-primary" @click="router.push('/sales/orders/new')">
          <svg viewBox="0 0 24 24" width="16" height="16" style="margin-right: 4px;">
            <path d="M12 5v14M5 12h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          {{ isZh ? '\u521b\u5efa\u9500\u552e\u8ba2\u5355' : 'Create Order' }}
        </button>
      </div>
    </div>

    <div class="filter-bar">
      <input type="text" class="form-input search-so" v-model="filter.salesOrderId" :placeholder="isZh ? '\u8ba2\u5355\u53f7' : 'Order No.'" />
      <input type="text" class="form-input search-cust" v-model="filter.customerName" :placeholder="isZh ? '\u5ba2\u6237\u540d\u79f0' : 'Customer Name'" />
      <select class="form-select search-st" v-model="filter.status">
        <option value="">{{ isZh ? '\u5168\u90e8\u72b6\u6001' : 'All Statuses' }}</option>
        <option value="OPEN">{{ isZh ? '\u6253\u5f00' : 'Open' }}</option>
        <option value="IN_PROCESS">{{ isZh ? '\u5904\u7406\u4e2d' : 'In Process' }}</option>
        <option value="COMPLETED">{{ isZh ? '\u5df2\u5b8c\u6210' : 'Completed' }}</option>
        <option value="CANCELLED">{{ isZh ? '\u5df2\u53d6\u6d88' : 'Cancelled' }}</option>
      </select>
      <button class="btn btn-primary" @click="fetchData">{{ isZh ? '\u67e5\u8be2' : 'Search' }}</button>
      <button class="btn btn-outline" @click="resetFilter">{{ isZh ? '\u91cd\u7f6e' : 'Reset' }}</button>
    </div>

    <div class="data-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>{{ isZh ? '\u8ba2\u5355\u53f7' : 'Order No.' }}</th>
            <th>{{ isZh ? '\u5ba2\u6237' : 'Customer' }}</th>
            <th>{{ isZh ? '\u8ba2\u5355\u65e5\u671f' : 'Order Date' }}</th>
            <th class="num">{{ isZh ? '\u51c0\u503c' : 'Net Value' }}</th>
            <th>{{ isZh ? '\u72b6\u6001' : 'Status' }}</th>
            <th>{{ isZh ? '\u64cd\u4f5c' : 'Action' }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.id" class="data-row">
            <td class="mono">{{ r.no }}</td>
            <td>{{ r.cust }}</td>
            <td>{{ r.date }}</td>
            <td class="num mono">{{ r.val }}</td>
            <td><span class="stag" :class="sc(r.st)">{{ r.stLabel }}</span></td>
            <td>
              <a class="link" @click="viewDetail(r.id)">{{ isZh ? '\u7f16\u8f91' : 'Edit' }}</a>
              <span class="divider" v-if="r.st === 'OPEN' || r.st === 'IN_PROCESS'">|</span>
              <a class="link" v-if="r.st === 'OPEN' || r.st === 'IN_PROCESS'" @click="convertToDelivery(r.id)">{{ isZh ? '\u8f6c\u4e3a\u53d1\u8d27\u5355' : 'Convert to Delivery' }}</a>
            </td>
          </tr>
          <tr v-if="rows.length === 0 && !loading">
            <td colspan="6" style="text-align:center;padding:40px;color:#999;">{{ isZh ? '\u672a\u627e\u5230\u9500\u552e\u8ba2\u5355\u3002' : 'No orders found.' }}</td>
          </tr>
          <tr v-if="loading">
            <td colspan="6" style="text-align:center;padding:40px;color:#999;">{{ isZh ? '\u52a0\u8f7d\u4e2d\u002e\u002e\u002e' : 'Loading...' }}</td>
          </tr>
        </tbody>
      </table>
      <div class="table-footer">
        <span class="tf-total">{{ isZh ? `\u5171 ${rows.length} \u6761` : `Total ${rows.length} items` }}</span>
        <div class="pager">
          <button class="pg-btn active">1</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { usePreferencesStore } from '@/stores/preferences'
import { alert, confirm } from "@/utils/toast"
import { fetchOrders, createDeliveryFromSalesOrder } from "@/api"

const router = useRouter()
const preferences = usePreferencesStore()
const isZh = computed(() => preferences.locale === 'zh')
interface R{id:string;no:string;cust:string;date:string;val:string;st:string}
const rows = ref<R[]>([])
const loading = ref(false)

const filter = reactive({
  salesOrderId: '',
  customerName: '',
  status: ''
})

const STATUS_LABELS_ZH: Record<string, string> = {
  OPEN: '\u6253\u5f00',
  IN_PROCESS: '\u5904\u7406\u4e2d',
  COMPLETED: '\u5df2\u5b8c\u6210',
  CANCELLED: '\u5df2\u53d6\u6d88'
}
const STATUS_LABELS_EN: Record<string, string> = {
  OPEN: 'Open',
  IN_PROCESS: 'In Process',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled'
}
function statusLabel(status: string) {
  return (isZh.value ? STATUS_LABELS_ZH : STATUS_LABELS_EN)[status] || status
}

async function fetchData() {
  loading.value = true
  try {
    const soData = await fetchOrders(filter)
    
    rows.value = (soData.items || []).map((i: any) => ({
      id: i.salesOrderId,
      no: i.salesOrderId,
      cust: i.customerId,
      date: i.createdTime?.split('T')[0] || 'N/A',
      val: `¥${(i.netValue || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      st: i.status,
      stLabel: statusLabel(i.status)
    }))
  } catch (err: any) {
    console.error("Fetch error:", err)
  } finally {
    loading.value = false
  }
}

function resetFilter() {
  Object.assign(filter, { salesOrderId: '', customerName: '', status: '' })
  fetchData()
}

onMounted(fetchData)

function sc(s:string){const m:Record<string,string>={"OPEN":"s-open","IN_PROCESS":"s-proc","COMPLETED":"s-done","CANCELLED":"s-cancel"};return m[s]||""}
function viewDetail(id:string){
  router.push(`/sales/order/${id}`)
}
async function convertToDelivery(id:string) {
  if (await confirm(isZh.value ? `\u662f\u5426\u4e3a\u9500\u552e\u8ba2\u5355 ${id} \u521b\u5efa\u53d1\u8d27\u5355\uff1f` : `Create delivery for order ${id}?`)) {
    try {
      const res = await createDeliveryFromSalesOrder(id)
      alert(isZh.value ? `\u53d1\u8d27\u5355 ${res.deliveryId} \u521b\u5efa\u6210\u529f\uff01` : `Delivery ${res.deliveryId} created successfully!`)
      router.push("/delivery/list")
    } catch (err: any) {
      alert((isZh.value ? '\u521b\u5efa\u53d1\u8d27\u5355\u5931\u8d25\uff1a' : 'Failed to create delivery: ') + err.message)
    }
  }
}
</script>

<style scoped>
.page{padding:28px 36px;max-width:1200px;margin:0 auto;}
.header-card{display:flex;align-items:center;background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:16px;padding:20px 24px;border:1px solid rgba(173,188,159,0.18);box-shadow:0 2px 8px rgba(173,188,159,0.12);margin-bottom:20px;}
.hc-left{display:flex;align-items:center;gap:14px;}
.hc-icon{width:44px;height:44px;border-radius:12px;background:rgba(67,104,80,0.08);display:flex;align-items:center;justify-content:center;}
.hc-title{font-size:18px;font-weight:800;color:#12372A;margin:0;}
.hc-sub{font-size:12px;color:rgba(18,55,42,0.45);margin:2px 0 0;}
.filter-bar{display:flex;gap:10px;margin-bottom:16px;align-items:center;flex-wrap:wrap;}
.search-so{width:140px;}
.search-cust{width:220px;}
.search-st{width:140px;}
.form-input,.form-select{height:38px;border:1px solid rgba(173,188,159,0.4);border-radius:8px;padding:0 12px;font-size:13px;color:#12372A;background:rgba(251,250,218,0.35);font-family:inherit;outline:none;transition:all 0.2s;}
.form-input:focus,.form-select:focus{border-color:#436850;box-shadow:0 0 0 3px rgba(67,104,80,0.06);}
.data-card{background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:14px;border:1px solid rgba(173,188,159,0.15);box-shadow:0 2px 6px rgba(173,188,159,0.1);overflow:hidden;}
.data-table{width:100%;border-collapse:collapse;font-size:13px;}
.data-table th{text-align:left;padding:12px 14px;font-size:10px;font-weight:700;color:rgba(18,55,42,0.45);text-transform:uppercase;letter-spacing:0.8px;background:rgba(173,188,159,0.08);border-bottom:1px solid rgba(173,188,159,0.2);}
.data-table th.num{text-align:right;}
.data-table td{padding:11px 14px;border-bottom:1px solid rgba(173,188,159,0.08);color:#12372A;}
.data-table td.num{text-align:right;}
.data-row:hover{background:rgba(67,104,80,0.025);}
.mono{font-family:'SF Mono',Consolas,monospace;font-size:12px;}
.stag{font-size:11px;font-weight:600;padding:4px 10px;border-radius:6px;}
.s-open{background:rgba(67,104,80,0.1);color:#436850;}
.s-proc{background:rgba(240,173,78,0.12);color:#c98a20;}
.s-done{background:rgba(67,104,80,0.12);color:#2d4a38;}
.s-cancel{background:rgba(217,83,79,0.08);color:#c94a45;}
.link{color:#436850;cursor:pointer;font-weight:600;font-size:12px;}
.link:hover{text-decoration:underline;}
.divider{margin:0 8px;color:rgba(18,55,42,0.15);font-size:12px;}
.table-footer{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-top:1px solid rgba(173,188,159,0.15);}
.tf-total{font-size:12px;color:rgba(18,55,42,0.4);}
.pager{display:flex;gap:4px;}
.pg-btn{min-width:30px;height:30px;border:1px solid rgba(173,188,159,0.25);border-radius:6px;background:rgba(251,250,218,0.3);font-size:12px;color:#12372A;cursor:pointer;display:flex;align-items:center;justify-content:center;}
.pg-btn.active{background:#436850;color:#FBFADA;border-color:#436850;}
.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 20px;font-size:13px;font-weight:600;border-radius:8px;cursor:pointer;transition:all 0.2s;font-family:inherit;}
.btn-primary{background:linear-gradient(135deg,#436850,#365440);color:#FBFADA;border:none;}
.btn-primary:hover{transform:translateY(-1px);}
.btn-outline{background:none;color:rgba(18,55,42,0.5);border:1px solid rgba(173,188,159,0.35);}
.btn-outline:hover{border-color:rgba(18,55,42,0.3);color:#12372A;}
</style>
