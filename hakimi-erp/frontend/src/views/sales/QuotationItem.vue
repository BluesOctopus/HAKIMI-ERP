<template>
  <MainLayout>
    <div class="page">
      <!-- Loading / Error -->
      <div v-if="loading" class="section-card" style="padding:40px;text-align:center;color:rgba(18,55,42,0.4)">
        Loading quotation data...
      </div>
      <div v-else-if="error" class="error-msg">{{ error }}</div>

      <template v-if="!loading">
        <!-- Top Bar -->
        <div class="top-bar">
          <div class="tb-left">
            <button class="tb-btn-icon" @click="$router.push('/')"><svg viewBox="0 0 20 20" width="16" height="16"><path d="M12 4l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
            <button class="tb-btn-icon" @click="$router.push('/')"><svg viewBox="0 0 20 20" width="16" height="16"><path d="M3 10l7-7 7 7M5 8v7a1 1 0 0 0 1 1h3v-4h2v4h3a1 1 0 0 0 1-1V8" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
            <span class="tb-title">Create Quotation: Item Data</span>
          </div>
          <button class="tb-btn-icon"><svg viewBox="0 0 20 20" width="15" height="15"><circle cx="9" cy="9" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M13 13l4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
        </div>

        <!-- Toolbar -->
        <div class="toolbar">
          <button class="tb-text" @click="deleteItem">Delete Item</button>
          <button class="tb-text" @click="showItemOutput">Item Output View</button>
          <button class="tb-text" @click="checkAvailability">Item Availability</button>
          <button class="tb-text">More &#9660;</button>
          <button class="tb-text" style="margin-left:auto" @click="$router.push('/sales/orders')">Exit</button>
        </div>

        <!-- Nav Arrows -->
        <div class="nav-row">
          <div class="nav-arrows">
            <button class="na-btn" @click="prevItem">&#171;</button><button class="na-btn" @click="prevItem">&#8249;</button>
            <span class="na-info">Item {{ currentItem }} / {{ totalItems }}</span>
            <button class="na-btn" @click="nextItem">&#8250;</button><button class="na-btn" @click="nextItem">&#187;</button>
          </div>
        </div>

        <!-- Header Fields with F4 Search -->
        <div class="form-card">
          <div class="hdr-info-row" v-if="inquiryId || customerId">
            <span class="info-tag" v-if="inquiryId">Ref Inquiry: {{ inquiryId }}</span>
            <span class="info-tag" v-if="customerId">Customer: {{ customerId }}</span>
          </div>
          <div class="hdr-field-row">
            <div class="hdr-field" v-if="!isFromInquiry">
              <label class="hf-label">Sold-to Party</label>
              <div class="input-with-f4-inline">
                <select class="hf-input" style="width:180px" v-model="customerId">
                  <option value="">-- Select --</option>
                  <option v-for="p in partners" :key="p.bp_id" :value="p.bp_id">{{ p.bp_id }} - {{ p.bp_name }}</option>
                </select>
                <button class="f4-trigger-sm" @click="openF4('soldToParty')" title="F4 Search"><svg viewBox="0 0 20 20" width="12" height="12"><circle cx="8" cy="8" r="5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 12l5 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
              </div>
            </div>
            <div class="hdr-field" v-else>
              <label class="hf-label">Sold-to Party</label>
              <div class="hf-input" style="width:180px;background:rgba(173,188,159,0.12);display:flex;align-items:center;padding-left:10px">{{ customerId }}</div>
            </div>
            <div class="hdr-field"><label class="hf-label">Sales Document Item</label><input type="text" class="hf-input" v-model="itemData.docItem" /></div>
            <div class="hdr-field">
              <label class="hf-label">Item category</label>
              <div class="input-with-f4-inline"><input type="text" class="hf-input" v-model="itemData.itemCat" /><button class="f4-trigger-sm" @click="openF4('itemCat')" title="F4 Search"><svg viewBox="0 0 20 20" width="12" height="12"><circle cx="8" cy="8" r="5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 12l5 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button></div>
              <span class="hf-hint">Standard Item</span>
            </div>
            <div class="hdr-field" style="flex:2">
              <label class="hf-label">Material</label>
              <div class="input-with-f4-inline">
                <select class="hf-input" style="width:180px" v-model="itemData.material">
                  <option value="">-- Select --</option>
                  <option v-for="m in materials" :key="m.material_id" :value="m.material_id">{{ m.material_id }} - {{ m.material_name }}</option>
                </select>
                <button class="f4-trigger-sm" @click="openF4('material')" title="F4 Search"><svg viewBox="0 0 20 20" width="12" height="12"><circle cx="8" cy="8" r="5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 12l5 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
              </div>
              <span class="hf-hint">{{ materialName }}</span>
            </div>
          </div>
        </div>

        <!-- Tabs -->
        <div class="form-card form-card-tabs">
          <div class="tab-bar">
            <button v-for="t in tabs" :key="t" class="tab-btn" :class="{active:activeTab===t}" @click="activeTab=t">{{ t }}</button>
          </div>

          <div class="tab-content" v-show="activeTab==='Conditions'">
            <div class="qnt-row">
              <div class="qnt-field"><label class="qnt-label">Quantity *</label><div class="qnt-input-wrap"><input type="text" class="qnt-input" v-model="qty" /><span class="qnt-unit">PC</span></div></div>
              <div class="qnt-field"><label class="qnt-label">Net</label><div class="qnt-readonly">{{ netPrice }}</div></div>
              <div class="qnt-field"><label class="qnt-label">Tax</label><input type="text" class="qnt-input" v-model="tax" /></div>
            </div>
            
            <!-- Pricing Toolbar -->
            <div class="price-toolbar">
              <div class="pt-left">
                <button class="pt-btn" title="Search" @click="openF4('pricing')"><svg viewBox="0 0 20 20" width="13" height="13"><circle cx="9" cy="9" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M13 13l4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
                <button class="pt-btn" title="Zoom In"><svg viewBox="0 0 20 20" width="13" height="13"><circle cx="9" cy="9" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M13 13l4 4M9 5v8M5 9h8" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg></button>
                <button class="pt-btn" title="Zoom Out"><svg viewBox="0 0 20 20" width="13" height="13"><circle cx="9" cy="9" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M13 13l4 4M5 9h8" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg></button>
                <button class="pt-text-btn" @click="showConditionRecord">Condition Record</button>
                <button class="pt-text-btn" @click="showAnalysis">Analysis</button>
              </div>
              <div class="pt-right">
                <button class="pt-text-btn" @click="updatePricing">Update</button>
                <button class="pt-btn" title="Settings"><svg viewBox="0 0 20 20" width="13" height="13"><circle cx="10" cy="10" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.9 4.9l1.4 1.4M13.7 13.7l1.4 1.4M4.9 15.1l1.4-1.4M13.7 6.3l1.4-1.4" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg></button>
              </div>
            </div>

            <!-- Pricing Table -->
            <div class="pricing-table-wrap">
              <table class="pricing-table">
                <thead><tr><th class="chk-col"></th><th>CN</th><th>Ty</th><th>Cond. Name</th><th>Description</th><th class="num">Amount</th><th>Crcy</th><th class="num">Unit</th><th class="num">Rate</th><th>Stat</th></tr></thead>
                <tbody>
                  <tr v-for="(r,i) in pricingRows" :key="i" :class="{derived:r.derived,total:r.total}">
                    <td class="chk-col"><input type="checkbox" :checked="r.active" /></td>
                    <td>{{ r.cn }}</td><td>{{ r.ty }}</td><td class="mono">{{ r.name }}</td><td>{{ r.desc }}</td>
                    <td class="num mono">{{ r.amount }}</td><td>{{ r.crcy }}</td><td class="num">{{ r.unit }}</td>
                    <td v-if="!r.total" class="num mono">{{ r.rate }}</td><td v-else></td>
                    <td v-if="!r.total"><span class="s-dot" :style="{color:r.statColor}">&#9679;</span></td><td v-else></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="tab-content" v-show="activeTab==='Sales A'">
            <div class="form-grid-3">
              <div class="hdr-field"><label class="hf-label">Sales Office</label><input type="text" class="hf-input" v-model="salesData.office" /></div>
              <div class="hdr-field"><label class="hf-label">Sales Group</label><input type="text" class="hf-input" v-model="salesData.group" /></div>
              <div class="hdr-field"><label class="hf-label">Order Reason</label><input type="text" class="hf-input" v-model="salesData.reason" /></div>
              <div class="hdr-field"><label class="hf-label">Usage</label><input type="text" class="hf-input" v-model="salesData.usage" /></div>
              <div class="hdr-field"><label class="hf-label">Delivery Date</label><input type="date" class="hf-input" v-model="salesData.delivDate" /></div>
            </div>
          </div>

          <div class="tab-content" v-show="activeTab==='Shipping'">
            <div class="form-grid-3">
              <div class="hdr-field"><label class="hf-label">Plant</label><input type="text" class="hf-input" v-model="shippingData.plant" /></div>
              <div class="hdr-field"><label class="hf-label">Shipping Point</label><input type="text" class="hf-input" v-model="shippingData.shippingPoint" /></div>
              <div class="hdr-field"><label class="hf-label">Storage Location</label><input type="text" class="hf-input" v-model="shippingData.storageLoc" /></div>
              <div class="hdr-field"><label class="hf-label">Delivery Priority</label><input type="text" class="hf-input" v-model="shippingData.priority" /></div>
              <div class="hdr-field"><label class="hf-label">Shipping Cond.</label><input type="text" class="hf-input" v-model="shippingData.condition" /></div>
            </div>
          </div>

          <div class="tab-content" v-show="activeTab==='Billing Document'">
            <div class="form-grid-3">
              <div class="hdr-field"><label class="hf-label">Payment Terms</label><input type="text" class="hf-input" v-model="billingData.payTerms" /></div>
              <div class="hdr-field"><label class="hf-label">Incoterms</label><input type="text" class="hf-input" v-model="billingData.incoterms" /></div>
              <div class="hdr-field"><label class="hf-label">Billing Block</label><input type="text" class="hf-input" v-model="billingData.block" /></div>
            </div>
          </div>

          <div class="tab-placeholder" v-show="!['Conditions','Sales A','Shipping','Billing Document'].includes(activeTab)">
            <p>{{ activeTab }} &mdash; content to be developed</p>
          </div>
        </div>

        <!-- Bottom Bar -->
        <div class="bottom-bar">
          <div class="bb-right">
            <button class="btn btn-cancel" @click="$router.push('/sales/orders')">Cancel</button>
            <button class="btn btn-primary" @click="saveQuotation" :disabled="saving">{{ saving ? 'Saving...' : 'Save' }}</button>
          </div>
        </div>
      </template>
    </div>

    <!-- F4 Search Modal -->
    <F4SearchModal
      :visible="f4Visible"
      :title="f4Title"
      :type="f4Type"
      @update:visible="f4Visible=$event"
      @select="onF4Select"
    />
    <SuccessModal
      v-model:visible="successVisible"
      title="Quotation Saved"
      :message="successMsg"
      @confirm="onSuccessConfirm"
    />
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from "vue"
import MainLayout from "@/layout/MainLayout.vue"
import F4SearchModal from "@/components/F4SearchModal.vue"
import SuccessModal from "@/components/SuccessModal.vue"
import { useRoute, useRouter } from "vue-router"
import {
  fetchPartners,
  fetchMaterials,
  fetchInquiryById,
  fetchQuotationById,
  createQuotation,
  updateQuotation
} from "@/api"
import type { Partner, Material } from "@/api/modules/master"
import type { Inquiry, Quotation } from "@/api/modules/sales"

const route = useRoute()
const router = useRouter()
const activeTab = ref("Conditions")
const tabs = ["Conditions","Sales A","Sales B","Shipping","Billing Document","Account Assignment","Schedule Lines"]

const currentItem = ref(1)
const totalItems = ref(1)
const qty = ref("1")
const tax = ref("13.00")
const quotationId = ref("")
const inquiryId = ref("")
const customerId = ref("")
const partners = ref<Partner[]>([])
const materials = ref<Material[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref("")
const successVisible = ref(false)
const successMsg = ref("")
const isFromInquiry = ref(false)

const materialMap = computed(() => {
  return materials.value.reduce((acc: Record<string, Material>, m: Material) => {
    if (m.material_id) acc[m.material_id] = m
    return acc
  }, {})
})
const materialName = computed(() => {
  return itemData.material ? materialMap.value[itemData.material]?.material_name || '' : ''
})

const salesData = reactive({
  office: "100",
  group: "10",
  reason: "",
  usage: "FREE",
  delivDate: ""
})

const shippingData = reactive({
  plant: "1000",
  shippingPoint: "1000",
  storageLoc: "0001",
  priority: "02",
  condition: "01"
})

const billingData = reactive({
  payTerms: "Z001",
  incoterms: "EXW",
  block: ""
})

const itemData = reactive({
  docItem: "10",
  itemCat: "AGN",
  material: "",
  materialName: ""
})

watch(() => itemData.material, (id) => {
  itemData.materialName = materialMap.value[id]?.material_name || ''
})

async function loadMasters() {
  const [bpRes, matRes] = await Promise.all([
    fetchPartners({ page_size: 100 }),
    fetchMaterials({ page_size: 100 })
  ])
  partners.value = bpRes.items || []
  materials.value = matRes.items || []
}

async function loadFromInquiry(id: string) {
  const res = await fetchInquiryById(id)
  const inq: Inquiry = res
  inquiryId.value = inq.inquiry_id
  customerId.value = inq.customer_id
  isFromInquiry.value = true
  if (inq.items && inq.items.length > 0) {
    const item = inq.items[0]
    itemData.material = item.material_id
    qty.value = String(item.order_quantity || 1)
    itemData.docItem = String(item.item_no || 10)
  }
  if (inq.requested_delivery_date) salesData.delivDate = inq.requested_delivery_date
}

async function loadFromQuotation(id: string) {
  const res = await fetchQuotationById(id)
  const q: Quotation = res
  quotationId.value = q.quotation_id
  inquiryId.value = q.inquiry_id || ''
  customerId.value = q.customer_id
  if (q.items && q.items.length > 0) {
    const item = q.items[0]
    itemData.material = item.material_id
    qty.value = String(item.order_quantity || 1)
    itemData.docItem = String(item.item_no || 10)
  }
  if (q.valid_to) salesData.delivDate = q.valid_to
  if (q.payment_terms) billingData.payTerms = q.payment_terms
  if (q.incoterms) billingData.incoterms = q.incoterms
}

async function load() {
  loading.value = true
  error.value = ""
  try {
    await loadMasters()
    const refInq = route.query.ref as string
    const qId = route.params.id as string
    if (qId && qId !== 'new') {
      await loadFromQuotation(qId)
    } else if (refInq) {
      await loadFromInquiry(refInq)
    }
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err.message || 'Failed to load quotation data'
    console.error("Load quotation data failed:", err)
  } finally {
    loading.value = false
  }
}

onMounted(load)

const netPrice = computed(() => {
  const q = parseFloat(qty.value) || 0
  return q > 0 ? (q * 3200).toLocaleString("zh-CN", { style: "currency", currency: "CNY" }) : "¥0.00"
})

const pricingRows = [
  {cn:"01",ty:"PR00",name:"Price",desc:"Standard Price",amount:"3,200.00",crcy:"CNY",unit:"1",rate:"3,200.00",active:true,derived:false,total:false,statColor:"#436850"},
  {cn:"02",ty:"K007",name:"Cust.Disc.",desc:"Customer Discount",amount:"160.00-",crcy:"CNY",unit:"1",rate:"5.000-",active:true,derived:false,total:false,statColor:"#D9534F"},
  {cn:"03",ty:"K005",name:"Vol.Disc.",desc:"Volume Discount",amount:"64.00-",crcy:"CNY",unit:"1",rate:"2.000-",active:true,derived:false,total:false,statColor:"#D9534F"},
  {cn:"04",ty:"MWST",name:"Tax",desc:"Output Tax 13%",amount:"386.88",crcy:"CNY",unit:"1",rate:"13.000",active:true,derived:false,total:false,statColor:"#436850"},
  {cn:"",ty:"",name:"Net",desc:"Net Value",amount:"2,976.00",crcy:"CNY",unit:"",rate:"",active:false,derived:true,total:false,statColor:""},
  {cn:"",ty:"",name:"Total",desc:"Total Value incl. Tax",amount:"3,362.88",crcy:"CNY",unit:"",rate:"",active:false,derived:false,total:true,statColor:""},
]

// F4 Search
const f4Visible = ref(false)
const f4Title = ref("Search Help")
const f4Type = ref('relationship')
const f4Context = ref("")

const f4Titles: Record<string, string> = {
  soldToParty: "Sold-to Party (1)",
  material: "Material Master (1)",
  itemCat: "Item Category (1)",
  pricing: "Pricing Conditions (1)",
}

function openF4(context: string) {
  f4Context.value = context
  f4Title.value = f4Titles[context] || "Search Help (1)"
  if (context === 'material') f4Type.value = 'material'
  else if (context === 'soldToParty') f4Type.value = 'partner'
  else f4Type.value = 'relationship'
  f4Visible.value = true
}
function onF4Select(item: any) {
  if (f4Context.value === 'material') {
    itemData.material = item.material_id
  } else if (f4Context.value === 'soldToParty') {
    customerId.value = item.bp_id
  }
  f4Visible.value = false
}

function showItemOutput(){ alert("Generating Output Document (PDF Simulation)...") }
function checkAvailability(){ 
  const q = parseFloat(qty.value) || 0
  alert(`ATP Check: Material ${itemData.material} is AVAILABLE. \nConfirmed Quantity: ${q} PC \nEarliest Delivery: ${new Date().toLocaleDateString()}`) 
}
function showConditionRecord(){ alert("Pricing Procedure: RVAA01 (Standard) \nCondition Record found for PR00.") }
function showAnalysis(){ alert("Pricing Analysis: \n- PR00: Base Price Active \n- K007: Cust. Discount Applied \n- MWST: Tax 13% Calculated") }
function updatePricing(){ 
  alert("Pricing updated based on current conditions!") 
}

function prevItem(){ if(currentItem.value>1)currentItem.value-- }
function nextItem(){ if(currentItem.value<totalItems.value)currentItem.value++ }
function deleteItem(){ if(confirm("Delete this item?"))alert("Item deleted") }

async function saveQuotation() {
  if (!customerId.value || !itemData.material) {
    alert("Please ensure Customer and Material are selected.")
    return
  }

  saving.value = true
  try {
    const q = parseFloat(qty.value) || 0
    const isEdit = !!quotationId.value
    const payload = {
      quotation_id: quotationId.value || `QUO${Math.floor(Math.random() * 1000000).toString().padStart(6, '0')}`,
      inquiry_id: inquiryId.value || null,
      quotation_type: 'QT',
      status: 'OPEN',
      customer_id: customerId.value,
      sold_to_party: customerId.value,
      ship_to_party: customerId.value,
      valid_from: new Date().toISOString().split('T')[0],
      valid_to: salesData.delivDate || null,
      payment_terms: billingData.payTerms,
      incoterms: billingData.incoterms,
      items: [
        {
          quotation_item_id: `QI${Math.floor(Math.random() * 1000000)}`,
          item_no: parseInt(itemData.docItem) || 10,
          material_id: itemData.material,
          order_quantity: q,
          sales_unit: 'PC',
          unit_price: 3200,
          net_price: 2976
        }
      ],
      net_value: 2976 * q
    }

    if (isEdit) {
      await updateQuotation(quotationId.value, payload)
    } else {
      await createQuotation(payload)
    }
    successMsg.value = `Quotation ${payload.quotation_id} ${isEdit ? 'updated' : 'created'} successfully!`
    successVisible.value = true
  } catch (err: any) {
    alert("Save failed: " + (err?.response?.data?.detail || err?.response?.data?.message || err.message))
  } finally {
    saving.value = false
  }
}

function onSuccessConfirm() {
  router.push("/sales/quotation")
}
</script>

<style scoped>
.page{padding:28px 36px;max-width:1200px;margin:0 auto;}
.error-msg {
  color: #D9534F;
  font-size: 13px;
  padding: 10px 14px;
  background: rgba(217, 83, 79, 0.08);
  border-radius: 8px;
  margin-bottom: 14px;
}
.top-bar{display:flex;align-items:center;justify-content:space-between;padding:10px 16px;background:linear-gradient(135deg,#2d4a38,#12372A);border-radius:10px;margin-bottom:8px;}
.tb-left{display:flex;align-items:center;gap:6px;}
.tb-btn-icon{width:32px;height:32px;border:none;border-radius:6px;background:transparent;color:rgba(251,250,218,0.7);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 0.2s;}
.tb-btn-icon:hover{background:rgba(251,250,218,0.1);color:#FBFADA;}
.tb-title{font-size:14px;font-weight:700;color:#FBFADA;margin-left:4px;}

.toolbar{display:flex;align-items:center;gap:2px;padding:6px 12px;background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:8px;border:1px solid rgba(173,188,159,0.15);margin-bottom:8px;}
.tb-text{padding:6px 12px;font-size:11px;color:rgba(18,55,42,0.55);background:none;border:none;cursor:pointer;font-family:inherit;border-radius:4px;transition:all 0.15s;}
.tb-text:hover{background:rgba(67,104,80,0.06);color:#436850;}

.nav-row{display:flex;align-items:center;justify-content:flex-end;margin-bottom:10px;}
.nav-arrows{display:flex;align-items:center;gap:2px;}
.na-btn{width:28px;height:28px;border:1px solid rgba(173,188,159,0.3);border-radius:5px;background:rgba(251,250,218,0.3);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;color:rgba(18,55,42,0.5);transition:all 0.2s;}
.na-btn:hover{border-color:#436850;color:#436850;}
.na-info{font-size:12px;color:rgba(18,55,42,0.4);margin:0 8px;}

.form-card{background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:12px;padding:16px 18px;border:1px solid rgba(173,188,159,0.15);box-shadow:0 1px 4px rgba(173,188,159,0.08);margin-bottom:12px;}
.hdr-info-row{display:flex;gap:12px;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid rgba(173,188,159,0.1);}
.form-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; padding: 10px 0; }
.info-tag{font-size:11px;font-weight:700;background:rgba(67,104,80,0.08);color:#436850;padding:4px 10px;border-radius:6px;border:1px solid rgba(67,104,80,0.1);}
.form-card-tabs{padding-top:0;overflow:hidden;}

.hdr-field-row{display:flex;gap:16px;}
.hdr-field{flex:1;display:flex;align-items:center;gap:10px;}
.hf-label{font-size:11px;font-weight:600;color:rgba(18,55,42,0.5);white-space:nowrap;}
.hf-input{height:32px;border:1px solid rgba(173,188,159,0.4);border-radius:6px;padding:0 10px;font-size:13px;color:#12372A;background:rgba(251,250,218,0.4);font-family:inherit;outline:none;width:100px;}
.hf-input:focus{border-color:#436850;box-shadow:0 0 0 3px rgba(67,104,80,0.05);}
.hf-hint{font-size:11px;color:rgba(18,55,42,0.3);}

.input-with-f4-inline{display:flex;align-items:center;gap:3px;}
.f4-trigger-sm{width:26px;height:26px;border:1px solid rgba(173,188,159,0.35);border-radius:5px;background:rgba(251,250,218,0.3);cursor:pointer;display:flex;align-items:center;justify-content:center;color:rgba(18,55,42,0.4);transition:all 0.2s;flex-shrink:0;}
.f4-trigger-sm:hover{border-color:#436850;color:#436850;background:rgba(67,104,80,0.06);}

.tab-bar{display:flex;gap:0;border-bottom:1px solid rgba(173,188,159,0.22);margin:0 -18px 16px;padding:0 18px;overflow-x:auto;background:rgba(251,250,218,0.15);border-radius:12px 12px 0 0;}
.tab-btn{padding:10px 12px;font-size:11px;font-weight:500;color:rgba(18,55,42,0.4);background:none;border:none;border-bottom:2px solid transparent;cursor:pointer;font-family:inherit;white-space:nowrap;transition:all 0.2s;}
.tab-btn:hover{color:#12372A;}
.tab-btn.active{color:#436850;font-weight:700;border-bottom-color:#436850;}

.tab-placeholder{display:flex;align-items:center;justify-content:center;min-height:120px;color:rgba(18,55,42,0.2);font-size:14px;padding-top:16px;}

.qnt-row{display:flex;gap:20px;margin-bottom:14px;}
.qnt-field{display:flex;flex-direction:column;gap:5px;}
.qnt-label{font-size:11px;font-weight:600;color:rgba(18,55,42,0.5);}
.qnt-input-wrap{display:flex;}
.qnt-input{height:34px;width:100px;border:1px solid rgba(173,188,159,0.4);border-radius:6px 0 0 6px;padding:0 10px;font-size:13px;color:#12372A;background:rgba(251,250,218,0.4);font-family:inherit;outline:none;}
.qnt-input:focus{border-color:#436850;}
.qnt-unit{display:flex;align-items:center;padding:0 10px;height:34px;font-size:12px;font-weight:600;color:rgba(18,55,42,0.45);background:rgba(173,188,159,0.12);border:1px solid rgba(173,188,159,0.4);border-left:none;border-radius:0 6px 6px 0;}
.qnt-readonly{display:flex;align-items:center;height:34px;padding:0 10px;font-size:13px;color:rgba(18,55,42,0.4);background:rgba(173,188,159,0.08);border-radius:6px;font-family:"SF Mono",Consolas,monospace;}

.price-toolbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;}
.pt-left,.pt-right{display:flex;align-items:center;gap:4px;}
.pt-btn{width:30px;height:30px;border:1px solid rgba(173,188,159,0.25);border-radius:6px;background:rgba(251,250,218,0.3);cursor:pointer;display:flex;align-items:center;justify-content:center;color:rgba(18,55,42,0.4);transition:all 0.2s;}
.pt-btn:hover{border-color:#436850;color:#436850;}
.pt-text-btn{padding:6px 12px;font-size:11px;color:rgba(18,55,42,0.5);background:none;border:1px solid rgba(173,188,159,0.2);border-radius:5px;cursor:pointer;font-family:inherit;transition:all 0.2s;}
.pt-text-btn:hover{color:#436850;border-color:#436850;}

.pricing-table-wrap{overflow-x:auto;border:1px solid rgba(173,188,159,0.12);border-radius:8px;}
.pricing-table{width:100%;border-collapse:collapse;font-size:12px;min-width:900px;}
.pricing-table th{text-align:left;padding:8px 8px;font-size:10px;font-weight:700;color:rgba(18,55,42,0.4);text-transform:uppercase;letter-spacing:0.5px;border-bottom:1px solid rgba(173,188,159,0.15);background:rgba(173,188,159,0.06);white-space:nowrap;}
.pricing-table th.num{text-align:right;}
.pricing-table th.chk-col{width:32px;text-align:center;}
.pricing-table td{padding:7px 8px;border-bottom:1px solid rgba(173,188,159,0.06);color:#12372A;white-space:nowrap;}
.pricing-table td.num{text-align:right;}
.pricing-table td.chk-col{text-align:center;}
.pricing-table td input[type=checkbox]{accent-color:#436850;cursor:pointer;}
.pricing-table tr:hover{background:rgba(67,104,80,0.02);}
.pricing-table tr.derived td{color:rgba(18,55,42,0.45);}
.pricing-table tr.total td{font-weight:700;color:#436850;}
.mono{font-family:"SF Mono",Consolas,monospace;font-size:11px;}
.s-dot{font-size:14px;}

.bottom-bar{background:linear-gradient(135deg,#2d4a38,#12372A);border-radius:0 0 12px 12px;padding:12px 18px;display:flex;justify-content:flex-end;gap:10px;}
.bb-right{display:flex;gap:10px;}
.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 22px;font-size:13px;font-weight:600;border-radius:8px;cursor:pointer;transition:all 0.2s;font-family:inherit;}
.btn-primary{background:#436850;color:#FBFADA;border:none;box-shadow:0 2px 6px rgba(0,0,0,0.2);}
.btn-primary:hover{background:#365440;}
.btn-primary:disabled{opacity:0.6;cursor:not-allowed;}
.btn-cancel{background:transparent;color:rgba(251,250,218,0.7);border:1px solid rgba(251,250,218,0.2);}
.btn-cancel:hover{background:rgba(251,250,218,0.05);color:#FBFADA;}
</style>
