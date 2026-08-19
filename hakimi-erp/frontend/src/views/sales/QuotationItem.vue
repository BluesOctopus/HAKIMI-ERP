<template>
  <div class="page-container">
    <!-- Header -->
    <div class="page-header">
        <h2 class="page-title">{{ isZh ? (isEdit ? '\u7f16\u8f91\u62a5\u4ef7' : '\u521b\u5efa\u62a5\u4ef7') : ((isEdit ? 'Edit' : 'Create') + ' Quotation') }}</h2>
        <button class="exit-btn" @click="handleExit">
          <svg viewBox="0 0 20 20" width="16" height="16">
            <path d="M6 6l8 8M14 6l-8 8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          {{ isZh ? '退出' : 'Exit' }}
        </button>
      </div>

      <!-- Main Form Area -->
      <div class="form-card">
        <div class="hdr-info-row" v-if="inquiryId">
          <span class="info-tag">{{ isZh ? '\u53c2\u8003\u8be2\u4ef7\uff1a' : 'Ref Inquiry: ' }}{{ inquiryId }}</span>
        </div>
        <div class="form-row form-row-3">
          <div class="form-group">
            <label class="form-label">{{ isZh ? '报价单号' : 'Quotation No.' }}</label>
            <input type="text" class="form-input" v-model="form.quotationId" :placeholder="isZh ? '留空自动生成' : 'Auto-generated if empty'" :disabled="isEdit" />
          </div>
          <div class="form-group">
            <label class="form-label required">{{ isZh ? '报价类型' : 'Quotation Type' }}</label>
            <select class="form-select" v-model="form.quotationType">
              <option value="QT">{{ isZh ? '报价 (QT)' : 'Quotation (QT)' }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label required">{{ isZh ? '客户（BP）' : 'Customer (BP)' }}</label>
            <div class="input-with-f4">
              <select class="form-select" v-model="form.customerId" :disabled="isFromInquiry">
                <option value="">{{ isZh ? '-- 选择客户 --' : '-- Select Customer --' }}</option>
                <option v-for="p in partners" :key="p.bpId" :value="p.bpId">{{ p.bpId }} - {{ p.bpName }}</option>
              </select>
              <button class="f4-trigger" @click="openF4('customer')" :disabled="isFromInquiry"><svg viewBox="0 0 20 20" width="14" height="14"><circle cx="9" cy="9" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M13 13l4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="form-card form-card-tabs">
        <div class="tab-bar">
          <button
            v-for="tab in tabs" :key="tab.key"
            class="tab-btn" :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >{{ tab.label }}</button>
        </div>

        <!-- Sales Tab -->
        <div class="tab-content" v-show="activeTab === 'sales'">
          <div class="form-grid-3">
            <div class="form-group">
              <label class="form-label">{{ isZh ? '销售组织' : 'Sales Org' }}</label>
              <input type="text" class="form-input" v-model="form.salesOrg" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ isZh ? '分销渠道' : 'Dist. Channel' }}</label>
              <input type="text" class="form-input" v-model="form.distributionChannel" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ isZh ? '产品组' : 'Division' }}</label>
              <input type="text" class="form-input" v-model="form.division" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ isZh ? '有效期自' : 'Valid From' }}</label>
              <input type="date" class="form-input" v-model="form.validFrom" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ isZh ? '有效期至' : 'Valid To' }}</label>
              <input type="date" class="form-input" v-model="form.validTo" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ isZh ? '币种' : 'Currency' }}</label>
              <input type="text" class="form-input" v-model="form.currency" />
            </div>
          </div>
        </div>

        <!-- Item Tab -->
        <div class="tab-content" v-show="activeTab === 'item'">
          <div class="form-grid-2">
            <div class="form-group">
              <label class="form-label required">{{ isZh ? '物料' : 'Material' }}</label>
              <div class="input-with-f4">
                <select class="form-select" v-model="itemForm.materialId">
                  <option value="">{{ isZh ? '-- 选择物料 --' : '-- Select Material --' }}</option>
                  <option v-for="m in materials" :key="m.materialId" :value="m.materialId">{{ m.materialId }} - {{ m.materialName }}</option>
                </select>
                <button class="f4-trigger" @click="openF4('material')"><svg viewBox="0 0 20 20" width="14" height="14"><circle cx="9" cy="9" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M13 13l4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">{{ isZh ? '行项目描述' : 'Item Description' }}</label>
              <input type="text" class="form-input" v-model="itemForm.itemDescription" />
            </div>
            <div class="form-group">
              <label class="form-label required">{{ isZh ? '数量' : 'Quantity' }}</label>
              <div class="input-with-unit">
                <input type="number" class="form-input" v-model="itemForm.orderQuantity" />
                <span class="input-unit">PC</span>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">{{ isZh ? '净价' : 'Net Price' }}</label>
              <div class="input-with-unit">
                <input type="number" class="form-input" v-model="itemForm.netPrice" />
                <span class="input-unit">CNY</span>
              </div>
            </div>
          </div>
          
          <div class="price-analysis">
            <button class="btn btn-outline btn-sm" @click="checkAvailability">{{ isZh ? '检查可用性' : 'Check Availability' }}</button>
            <button class="btn btn-outline btn-sm" @click="showAnalysis">{{ isZh ? '定价分析' : 'Pricing Analysis' }}</button>
          </div>
        </div>

        <!-- Billing Tab -->
        <div class="tab-content" v-show="activeTab === 'billing'">
          <div class="form-grid-3">
            <div class="form-group">
              <label class="form-label">{{ isZh ? '付款条件' : 'Payment Terms' }}</label>
              <input type="text" class="form-input" v-model="form.paymentTerms" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ isZh ? '贸易条款' : 'Incoterms' }}</label>
              <input type="text" class="form-input" v-model="form.incoterms" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ isZh ? '交货工厂' : 'Delivering Plant' }}</label>
              <input type="text" class="form-input" v-model="form.deliveringPlant" />
            </div>
          </div>
        </div>

        <div class="tab-content tab-placeholder" v-show="!['sales','item','billing'].includes(activeTab)">
          <p>{{ activeTabLabel }} &mdash; {{ isZh ? '功能待开发' : 'content to be developed' }}</p>
        </div>
      </div>

      <!-- Action Bar -->
      <div class="action-bar">
        <div class="action-left">
          <button class="btn btn-primary" @click="handleSave" :disabled="saving">
            <svg viewBox="0 0 20 20" width="16" height="16">
              <path d="M4 16V4a1 1 0 0 1 1-1h8l4 4v9a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z" fill="none" stroke="currentColor" stroke-width="1.5"/>
              <path d="M13 3v4h4M7 12h6M7 15h4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            {{ isZh ? (saving ? '\u4fdd\u5b58\u4e2d...' : '\u4fdd\u5b58') : (saving ? 'Saving...' : 'Save') }}
          </button>
          <button class="btn btn-secondary" @click="handleSaveContinue" :disabled="saving" v-if="!isEdit">
            {{ isZh ? '\u4fdd\u5b58\u5e76\u7ee7\u7eed' : 'Save & Continue' }}
          </button>
          <button class="btn btn-outline" @click="convertToOrder" v-if="isEdit && form.status === 'OPEN'">
            {{ isZh ? '转为销售订单' : 'Convert to Order' }}
          </button>
        </div>
        <button class="btn btn-border" @click="handleExit" :disabled="saving">{{ isZh ? '取消' : 'Cancel' }}</button>
      </div>

      <!-- Recent Quotations -->
      <div class="form-card" style="margin-top: 30px;">
        <h3 class="block-title">{{ isZh ? '最近报价' : 'Recent Quotations' }}</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>{{ isZh ? '客户' : 'Customer' }}</th>
              <th>{{ isZh ? '有效期至' : 'Valid Until' }}</th>
              <th>{{ isZh ? '净值' : 'Net Value' }}</th>
              <th>{{ isZh ? '状态' : 'Status' }}</th>
              <th>{{ isZh ? '操作' : 'Action' }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in recentQuotations" :key="q.quotationId">
              <td class="mono">{{ q.quotationId }}</td>
              <td>{{ q.customerId }}</td>
              <td>{{ q.validTo || 'N/A' }}</td>
              <td class="num">¥{{ q.netValue?.toLocaleString() }}</td>
              <td><span class="status-tag">{{ q.status }}</span></td>
              <td><a class="link-btn" @click="loadQuotation(q.quotationId)">{{ isZh ? '编辑' : 'Edit' }}</a></td>
            </tr>
          </tbody>
        </table>
      </div>
    <F4SearchModal v-model:visible="showF4" :type="f4Type" @select="onF4Select" />
    <SuccessModal v-model:visible="successVisible" :message="successMsg" @confirm="onSuccessConfirm" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePreferencesStore } from '@/stores/preferences'
import F4SearchModal from '@/components/F4SearchModal.vue'
import SuccessModal from '@/components/SuccessModal.vue'
import { alert } from '@/utils/toast'
import {
  fetchQuotations,
  fetchQuotationById,
  createQuotation,
  updateQuotation,
  fetchInquiryById,
  fetchPartners,
  fetchMaterials
} from '@/api'

const router = useRouter()
const route = useRoute()
const preferences = usePreferencesStore()
const isZh = computed(() => preferences.locale === 'zh')

const loading = ref(false)
const saving = ref(false)
const isEdit = computed(() => !!route.params.id && route.params.id !== 'new')
const isFromInquiry = computed(() => !!route.query.ref)
const inquiryId = ref(route.query.ref as string || '')
const activeTab = ref('sales')
const showF4 = ref(false)
const f4Type = ref('partner')
const f4Field = ref('')

const successVisible = ref(false)
const successMsg = ref('')

const partners = ref<any[]>([])
const materials = ref<any[]>([])
const recentQuotations = ref<any[]>([])

const tabs = computed(() => isZh.value
  ? [
    { key: 'sales', label: '销售数据' },
    { key: 'item', label: '行项目概览' },
    { key: 'billing', label: '开票' },
    { key: 'conditions', label: '条件' },
    { key: 'partners', label: '合作伙伴' },
  ]
  : [
    { key: 'sales', label: 'Sales Data' },
    { key: 'item', label: 'Item Overview' },
    { key: 'billing', label: 'Billing' },
    { key: 'conditions', label: 'Conditions' },
    { key: 'partners', label: 'Partners' },
  ])

const activeTabLabel = computed(() => tabs.value.find(t => t.key === activeTab.value)?.label || '')

const form = reactive({
  quotationId: '',
  quotationType: 'QT',
  inquiryId: '',
  customerId: '',
  salesOrg: '1000',
  distributionChannel: '10',
  division: '00',
  salesOffice: '100',
  salesGroup: '10',
  currency: 'CNY',
  validFrom: new Date().toISOString().split('T')[0],
  validTo: '',
  deliveringPlant: '1000',
  incoterms: 'EXW',
  paymentTerms: 'Z001',
  status: 'OPEN',
  netValue: 0
})

const itemForm = reactive({
  materialId: '',
  itemDescription: '',
  orderQuantity: 1,
  unitPrice: 0,
  netPrice: 0
})

async function loadMasters() {
  const [bpRes, matRes, qRes] = await Promise.all([
    fetchPartners({ limit: 1000 }),
    fetchMaterials({ limit: 1000 }),
    fetchQuotations({ limit: 5 })
  ])
  partners.value = bpRes.items || []
  materials.value = matRes.items || []
  recentQuotations.value = qRes.items || []
}

async function loadQuotation(id: string) {
  loading.value = true
  try {
    const data = await fetchQuotationById(id)
    Object.assign(form, data)
    if (data.items && data.items.length > 0) {
      Object.assign(itemForm, data.items[0])
    }
  } catch (err: any) {
    alert(isZh.value ? '加载报价失败：' + err.message : 'Failed to load quotation: ' + err.message)
  } finally {
    loading.value = false
  }
}

async function loadFromInquiry(id: string) {
  loading.value = true
  try {
    const data = await fetchInquiryById(id)
    form.customerId = data.customerId
    form.inquiryId = data.inquiryId
    form.salesOrg = data.salesOrg || '1000'
    form.distributionChannel = data.distributionChannel || '10'
    form.division = data.division || '00'
    form.currency = data.currency || 'CNY'
    form.paymentTerms = data.paymentTerms || 'Z001'
    form.incoterms = data.incoterms || 'EXW'
    
    if (data.items && data.items.length > 0) {
      const item = data.items[0]
      itemForm.materialId = item.materialId
      itemForm.itemDescription = item.itemDescription
      itemForm.orderQuantity = item.orderQuantity
      itemForm.unitPrice = item.unitPrice || 0
      itemForm.netPrice = item.netPrice || item.unitPrice || 0
    }
  } catch (err: any) {
    alert(isZh.value ? '加载询价参考失败：' + err.message : 'Failed to load inquiry reference: ' + err.message)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadMasters()
  if (isEdit.value) {
    await loadQuotation(route.params.id as string)
  } else if (inquiryId.value) {
    await loadFromInquiry(inquiryId.value)
  }
})

async function handleSave() {
  if (!form.customerId || !itemForm.materialId) {
    alert(isZh.value ? '请填写必填项：客户和物料' : 'Please fill in required fields: Customer and Material')
    return
  }
  saving.value = true
  try {
    const cleanForm = Object.fromEntries(
      Object.entries(form).map(([k, v]) => [k, v === '' ? null : v])
    )
    const payload = {
      ...cleanForm,
      quotationId: form.quotationId || `QUO${Math.floor(Math.random() * 1000000).toString().padStart(6, '0')}`,
      inquiryId: inquiryId.value || form.inquiryId || null,
      items: [
        {
          quotationItemId: `QI${Math.floor(Math.random() * 1000000)}`,
          itemNo: 10,
          ...itemForm,
          salesUnit: 'PC'
        }
      ],
      netValue: itemForm.netPrice * itemForm.orderQuantity
    }
    
    if (isEdit.value) {
      await updateQuotation(form.quotationId, payload)
      successMsg.value = isZh.value ? `报价单 ${form.quotationId} 更新成功！` : `Quotation ${form.quotationId} updated successfully!`
    } else {
      await createQuotation(payload)
      successMsg.value = isZh.value ? `报价单 ${payload.quotationId} 创建成功！` : `Quotation ${payload.quotationId} created successfully!`
    }
    successVisible.value = true
  } catch (err: any) {
    alert(isZh.value ? '保存失败：' + err.message : 'Save failed: ' + err.message)
  } finally {
    saving.value = false
  }
}

function handleSaveContinue() {
  handleSave()
}

function onSuccessConfirm() {
  successVisible.value = false
  if (!isEdit.value) {
    router.push('/sales/quotation')
  }
}

function handleExit() {
  router.push('/sales/quotation')
}

function convertToOrder() {
  router.push({ path: '/sales/orders/new', query: { ref: form.quotationId } })
}

function openF4(field: string) {
  f4Field.value = field
  f4Type.value = field === 'material' ? 'material' : 'partner'
  showF4.value = true
}

function onF4Select(item: any) {
  if (f4Field.value === 'customer') {
    form.customerId = item.bpId
  } else if (f4Field.value === 'material') {
    itemForm.materialId = item.materialId
  }
  showF4.value = false
}

function checkAvailability() {
  alert(isZh.value ? `可用性检查：物料 ${itemForm.materialId} 可用。` : `ATP Check: Material ${itemForm.materialId} is AVAILABLE.`)
}

function showAnalysis() {
  alert(isZh.value ? '定价分析：PR00 基础价，K007 折扣，MWST 税。' : "Pricing Analysis: PR00 Base Price, K007 Discount, MWST Tax.")
}
</script>

<style scoped>
.page-container { padding: 32px 40px; max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-title { font-size: 20px; font-weight: 700; color: #12372A; margin: 0; }
.exit-btn { display: inline-flex; align-items: center; gap: 6px; background: none; border: 1px solid rgba(173,188,159,0.4); border-radius: 8px; padding: 8px 18px; font-size: 13px; color: rgba(18,55,42,0.6); cursor: pointer; transition: all 0.2s; font-family: inherit; }
.exit-btn:hover { border-color: #D9534F; color: #D9534F; background: rgba(217,83,79,0.04); }

.form-card { background: linear-gradient(145deg, #fdfce8, #f7f5d1); border-radius: 14px; padding: 24px; margin-bottom: 20px; border: 1px solid rgba(173, 188, 159, 0.18); box-shadow: 0 2px 6px rgba(173, 188, 159, 0.12); }
.form-card-tabs { padding-top: 0; overflow: hidden; }

.hdr-info-row { display: flex; gap: 12px; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid rgba(173,188,159,0.1); }
.info-tag { font-size: 11px; font-weight: 700; background: rgba(67,104,80,0.08); color:#436850; padding:4px 10px; border-radius:6px; border:1px solid rgba(67,104,80,0.1); }

.form-row { display: grid; gap: 18px; margin-bottom: 16px; }
.form-row-3 { grid-template-columns: 1fr 1fr 1fr; }
.form-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; padding: 20px 0; }
.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; padding: 20px 0; }

.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 12px; font-weight: 600; color: rgba(18, 55, 42, 0.7); letter-spacing: 0.3px; }
.form-label.required::after { content: ' *'; color: #D9534F; font-weight: 700; }
.form-input, .form-select { height: 38px; border: 1px solid rgba(173,188,159,0.4); border-radius: 8px; padding: 0 12px; font-size: 13px; color: #12372A; background: rgba(251, 250, 218, 0.4); font-family: inherit; transition: all 0.2s; outline: none; width: 100%; }
.form-input:focus, .form-select:focus { border-color: #436850; box-shadow: 0 0 0 3px rgba(67, 104, 80, 0.08); background: #fff; }

.input-with-f4 { position: relative; display: flex; gap: 4px; }
.f4-trigger { width: 38px; height: 38px; border: 1px solid rgba(173,188,159,0.4); border-radius: 8px; background: rgba(251, 250, 218, 0.4); cursor: pointer; display: flex; align-items: center; justify-content: center; color: rgba(18,55,42,0.5); }
.f4-trigger:hover { border-color: #436850; color: #436850; background: #fff; }

.input-with-unit { position: relative; display: flex; }
.input-unit { display: flex; align-items: center; padding: 0 12px; background: rgba(173,188,159,0.1); border: 1px solid rgba(173,188,159,0.4); border-left: none; border-radius: 0 8px 8px 0; font-size: 12px; font-weight: 600; color: #436850; }
.input-with-unit .form-input { border-radius: 8px 0 0 8px; }

.tab-bar { display: flex; gap: 0; border-bottom: 1px solid rgba(173,188,159,0.3); margin: 0 -24px; padding: 0 24px; background: rgba(251, 250, 218, 0.3); border-radius: 14px 14px 0 0; }
.tab-btn { padding: 12px 18px; font-size: 12px; font-weight: 500; color: rgba(18, 55, 42, 0.5); background: none; border: none; border-bottom: 2px solid transparent; cursor: pointer; transition: all 0.2s; font-family: inherit; white-space: nowrap; }
.tab-btn.active { color: #436850; font-weight: 600; border-bottom-color: #436850; background: linear-gradient(to bottom, transparent, rgba(67, 104, 80, 0.04)); }

.tab-content { padding-top: 22px; }
.tab-placeholder { display: flex; align-items: center; justify-content: center; min-height: 120px; color: rgba(18,55,42,0.2); font-size: 14px; }

.price-analysis { margin-top: 10px; display: flex; gap: 10px; }

.action-bar { display: flex; align-items: center; justify-content: space-between; padding: 18px 24px; background: linear-gradient(145deg, #fdfce8, #f7f5d1); border-radius: 14px; border: 1px solid rgba(173, 188, 159, 0.18); box-shadow: 0 2px 6px rgba(173, 188, 159, 0.12); }
.action-left { display: flex; gap: 12px; }
.btn { display: inline-flex; align-items: center; gap: 8px; padding: 11px 24px; font-size: 13px; font-weight: 600; border-radius: 8px; cursor: pointer; transition: all 0.2s; font-family: inherit; }
.btn-sm { padding: 6px 14px; font-size: 11px; }
.btn-primary { background: linear-gradient(135deg, #436850, #365440); color: #FBFADA; border: none; }
.btn-secondary { background: none; color: #436850; border: 1px solid #436850; }
.btn-border { background: none; color: rgba(18,55,42,0.5); border: 1px solid rgba(173,188,159,0.4); }
.btn-outline { background: none; color: #436850; border: 1px solid rgba(67, 104, 80, 0.3); }

.block-title { font-size: 13px; font-weight: 700; color: #436850; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
.block-title::before { content: ''; width: 4px; height: 14px; background: #436850; border-radius: 2px; display: inline-block; }

.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 12px; font-size: 11px; color: rgba(18, 55, 42, 0.4); text-transform: uppercase; border-bottom: 1px solid rgba(173,188,159,0.2); }
.data-table td { padding: 12px; color: #12372A; border-bottom: 1px solid rgba(173,188,159,0.08); }
.data-table td.num { text-align: right; font-family: monospace; }
.mono { font-family: monospace; }
.status-tag { background: rgba(67, 104, 80, 0.1); color: #436850; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.link-btn { color: #436850; cursor: pointer; font-weight: 600; }
.link-btn:hover { text-decoration: underline; }
</style>
