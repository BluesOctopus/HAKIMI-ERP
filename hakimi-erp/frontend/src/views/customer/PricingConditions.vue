<template>
  <MainLayout>
    <div class="workspace-page">
      <header class="page-header">
        <div class="header-identity">
          <span class="header-icon"><Coin /></span>
          <div>
            <h1 class="page-title">Pricing Conditions</h1>
            <p class="page-subtitle">Condition records, sales scope, scales, validity, and calculation controls</p>
          </div>
        </div>
        <div class="header-actions">
          <span class="mode-pill">{{ selectedConditionId ? 'Display / Edit' : 'Create' }}</span>
          <button class="secondary-button" type="button" @click="startNewCondition">
            <Plus />
            New Condition
          </button>
        </div>
      </header>

      <section class="workspace-panel record-header" aria-label="Pricing condition key fields">
        <div class="key-grid">
          <label class="field">
            <span class="field-label required">Condition Record ID</span>
            <input v-model.trim="form.conditionId" class="control mono" placeholder="e.g. PC-10001" />
          </label>
          <label class="field">
            <span class="field-label required">Condition Type</span>
            <select v-model="form.conditionType" class="control">
              <option value="PR00">PR00 - Base Price</option>
              <option value="K004">K004 - Material Discount</option>
              <option value="K005">K005 - Customer / Material Discount</option>
              <option value="K007">K007 - Customer Discount</option>
              <option value="KF00">KF00 - Freight</option>
              <option value="MWST">MWST - Output Tax</option>
              <option value="RA01">RA01 - Percentage Discount</option>
              <option value="ZPR1">ZPR1 - Custom Price</option>
            </select>
          </label>
          <label class="field">
            <span class="field-label">Application</span>
            <select v-model="form.application" class="control">
              <option value="V">V - Sales and Distribution</option>
              <option value="M">M - Purchasing</option>
            </select>
          </label>
          <label class="field">
            <span class="field-label">Status</span>
            <select v-model="form.status" class="control">
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
              <option value="DRAFT">Draft</option>
            </select>
          </label>
        </div>
      </section>

      <section class="workspace-panel tab-shell" aria-label="Pricing condition details">
        <nav class="tab-bar" aria-label="Pricing condition data views">
          <button
            v-for="tab in tabs"
            :key="tab"
            class="tab-button"
            :class="{ active: activeTab === tab }"
            type="button"
            @click="activeTab = tab"
          >
            {{ tab }}
          </button>
        </nav>

        <div v-show="activeTab === 'Condition Record'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Condition Data</legend>
            <div class="field-grid">
              <label class="field span-2">
                <span class="field-label required">Condition Name</span>
                <input v-model.trim="form.conditionName" class="control" placeholder="Condition description" />
              </label>
              <label class="field">
                <span class="field-label">Calculation Type</span>
                <select v-model="form.calculationType" class="control">
                  <option value="AMOUNT">Fixed Amount</option>
                  <option value="PERCENT">Percentage</option>
                  <option value="QUANTITY">Quantity Based</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Condition Category</span>
                <select v-model="form.conditionCategory" class="control">
                  <option value="PRICE">Price</option>
                  <option value="DISCOUNT">Discount / Surcharge</option>
                  <option value="FREIGHT">Freight</option>
                  <option value="TAX">Tax</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Amount</span>
                <div class="input-affix">
                  <input v-model="form.amount" class="control" type="number" step="0.01" />
                  <span class="affix">{{ form.currency }}</span>
                </div>
              </label>
              <label class="field">
                <span class="field-label">Rate</span>
                <div class="input-affix">
                  <input v-model="form.rate" class="control" type="number" step="0.01" />
                  <span class="affix">%</span>
                </div>
              </label>
              <label class="field">
                <span class="field-label">Currency</span>
                <select v-model="form.currency" class="control">
                  <option>CNY</option>
                  <option>USD</option>
                  <option>EUR</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Pricing Unit</span>
                <div class="input-affix">
                  <input v-model="form.pricingUnit" class="control" type="number" min="1" step="1" />
                  <span class="affix">{{ form.unitOfMeasure }}</span>
                </div>
              </label>
            </div>
          </fieldset>
          <fieldset class="form-section">
            <legend class="section-title">Unit and Usage</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Unit of Measure</span>
                <select v-model="form.unitOfMeasure" class="control">
                  <option>EA</option>
                  <option>KG</option>
                  <option>BOX</option>
                  <option>PAL</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Condition Usage</span>
                <select v-model="form.conditionUsage" class="control">
                  <option value="A">A - Pricing</option>
                  <option value="B">B - Rebate</option>
                  <option value="E">E - Bonus Buy</option>
                </select>
              </label>
              <div class="field span-2">
                <span class="field-label">Entry Controls</span>
                <div class="check-row">
                  <label class="check-control"><input v-model="form.manualEntry" type="checkbox" /> Manual entry allowed</label>
                  <label class="check-control"><input v-model="form.headerCondition" type="checkbox" /> Header condition</label>
                  <label class="check-control"><input v-model="form.itemCondition" type="checkbox" /> Item condition</label>
                </div>
              </div>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Scope'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Sales Area</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Sales Organization</span>
                <select v-model="form.salesOrg" class="control">
                  <option value="*">* - All Organizations</option>
                  <option value="1000">1000 - Domestic Sales</option>
                  <option value="2000">2000 - Export Sales</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Distribution Channel</span>
                <select v-model="form.distributionChannel" class="control">
                  <option value="*">* - All Channels</option>
                  <option value="10">10 - Direct Sales</option>
                  <option value="20">20 - Wholesale</option>
                  <option value="30">30 - Online</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Division</span>
                <select v-model="form.division" class="control">
                  <option value="*">* - All Divisions</option>
                  <option value="00">00 - Cross Division</option>
                  <option value="10">10 - Standard Products</option>
                  <option value="20">20 - Services</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Price List</span>
                <select v-model="form.priceList" class="control">
                  <option value="*">* - All Price Lists</option>
                  <option value="01">01 - Standard</option>
                  <option value="02">02 - Wholesale</option>
                  <option value="03">03 - Export</option>
                </select>
              </label>
            </div>
          </fieldset>
          <fieldset class="form-section">
            <legend class="section-title">Business Object Scope</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Material</span>
                <input v-model.trim="form.materialId" class="control mono" placeholder="* for all materials" />
              </label>
              <label class="field">
                <span class="field-label">Business Partner</span>
                <input v-model.trim="form.businessPartnerId" class="control mono" placeholder="* for all partners" />
              </label>
              <label class="field">
                <span class="field-label">Customer Group</span>
                <select v-model="form.customerGroup" class="control">
                  <option value="*">* - All Customer Groups</option>
                  <option value="01">01 - Retail</option>
                  <option value="02">02 - Wholesale</option>
                  <option value="03">03 - Key Accounts</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Material Pricing Group</span>
                <select v-model="form.materialPricingGroup" class="control">
                  <option value="*">* - All Pricing Groups</option>
                  <option value="01">01 - Standard</option>
                  <option value="02">02 - Promotion</option>
                </select>
              </label>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Scales'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Scale Definition</legend>
            <div class="field-grid cols-3">
              <label class="field">
                <span class="field-label">Scale Basis</span>
                <select v-model="form.scaleBasis" class="control">
                  <option value="QUANTITY">Quantity</option>
                  <option value="VALUE">Value</option>
                  <option value="WEIGHT">Gross Weight</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Scale Type</span>
                <select v-model="form.scaleType" class="control">
                  <option value="FROM">From Scale</option>
                  <option value="TO">To Scale</option>
                  <option value="GRADUATED">Graduated Scale</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Scale UoM</span>
                <select v-model="form.scaleUom" class="control">
                  <option>EA</option>
                  <option>KG</option>
                  <option>BOX</option>
                </select>
              </label>
            </div>
          </fieldset>
          <fieldset class="form-section">
            <legend class="section-title">Scale Lines</legend>
            <div class="scale-table">
              <div class="scale-heading">From Quantity</div>
              <div class="scale-heading">Amount</div>
              <div class="scale-heading">Rate</div>
              <input v-model="form.scale1Qty" class="control" type="number" min="0" step="1" aria-label="Scale line 1 quantity" />
              <input v-model="form.scale1Amount" class="control" type="number" step="0.01" aria-label="Scale line 1 amount" />
              <input v-model="form.scale1Rate" class="control" type="number" step="0.01" aria-label="Scale line 1 rate" />
              <input v-model="form.scale2Qty" class="control" type="number" min="0" step="1" aria-label="Scale line 2 quantity" />
              <input v-model="form.scale2Amount" class="control" type="number" step="0.01" aria-label="Scale line 2 amount" />
              <input v-model="form.scale2Rate" class="control" type="number" step="0.01" aria-label="Scale line 2 rate" />
              <input v-model="form.scale3Qty" class="control" type="number" min="0" step="1" aria-label="Scale line 3 quantity" />
              <input v-model="form.scale3Amount" class="control" type="number" step="0.01" aria-label="Scale line 3 amount" />
              <input v-model="form.scale3Rate" class="control" type="number" step="0.01" aria-label="Scale line 3 rate" />
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Validity'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Validity Period</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label required">Valid From</span>
                <input v-model="form.validFrom" class="control" type="date" />
              </label>
              <label class="field">
                <span class="field-label required">Valid To</span>
                <input v-model="form.validTo" class="control" type="date" />
              </label>
              <label class="field">
                <span class="field-label">Release Status</span>
                <select v-model="form.releaseStatus" class="control">
                  <option value="RELEASED">Released</option>
                  <option value="BLOCKED">Blocked</option>
                  <option value="REVIEW">Under Review</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Pricing Date Category</span>
                <select v-model="form.pricingDateCategory" class="control">
                  <option value="ORDER">Order Date</option>
                  <option value="DELIVERY">Delivery Date</option>
                  <option value="BILLING">Billing Date</option>
                </select>
              </label>
            </div>
          </fieldset>
          <fieldset class="form-section">
            <legend class="section-title">Period Controls</legend>
            <div class="check-row">
              <label class="check-control"><input v-model="form.exclusive" type="checkbox" /> Exclusive condition</label>
              <label class="check-control"><input v-model="form.autoExtend" type="checkbox" /> Auto-extend validity</label>
              <label class="check-control"><input v-model="form.deletionFlag" type="checkbox" /> Mark for deletion</label>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Calculation'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Calculation Controls</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Pricing Procedure</span>
                <select v-model="form.pricingProcedure" class="control">
                  <option value="RVAA01">RVAA01 - Standard</option>
                  <option value="ZVAA01">ZVAA01 - Domestic</option>
                  <option value="ZEXP01">ZEXP01 - Export</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Access Sequence</span>
                <select v-model="form.accessSequence" class="control">
                  <option value="PR00">PR00 - Price</option>
                  <option value="K004">K004 - Material Discount</option>
                  <option value="K005">K005 - Customer / Material Discount</option>
                  <option value="K007">K007 - Customer Discount</option>
                  <option value="RA01">RA01 - Percentage Discount</option>
                  <option value="ZPR1">ZPR1 - Custom Price</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Rounding Rule</span>
                <select v-model="form.roundingRule" class="control">
                  <option value="COMMERCIAL">Commercial Rounding</option>
                  <option value="UP">Round Up</option>
                  <option value="DOWN">Round Down</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Decimal Places</span>
                <select v-model="form.decimalPlaces" class="control">
                  <option value="0">0</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Minimum Value</span>
                <input v-model="form.minimumValue" class="control" type="number" step="0.01" />
              </label>
              <label class="field">
                <span class="field-label">Maximum Value</span>
                <input v-model="form.maximumValue" class="control" type="number" step="0.01" />
              </label>
              <div class="field span-2">
                <span class="field-label">Calculation Flags</span>
                <div class="check-row">
                  <label class="check-control"><input v-model="form.statistical" type="checkbox" /> Statistical</label>
                  <label class="check-control"><input v-model="form.accrual" type="checkbox" /> Accruals</label>
                  <label class="check-control"><input v-model="form.groupCondition" type="checkbox" /> Group condition</label>
                </div>
              </div>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Approval'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Approval Assignment</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Approval Status</span>
                <select v-model="form.approvalStatus" class="control">
                  <option value="NOT_REQUIRED">Not Required</option>
                  <option value="PENDING">Pending</option>
                  <option value="APPROVED">Approved</option>
                  <option value="REJECTED">Rejected</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Approver Group</span>
                <select v-model="form.approverGroup" class="control">
                  <option value="SALES_MGR">Sales Management</option>
                  <option value="PRICING">Pricing Team</option>
                  <option value="FINANCE">Finance Control</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Release Code</span>
                <input v-model.trim="form.releaseCode" class="control mono" placeholder="Release code" />
              </label>
              <label class="field">
                <span class="field-label">Change Reason</span>
                <select v-model="form.changeReason" class="control">
                  <option value="NEW">New Condition</option>
                  <option value="MARKET">Market Adjustment</option>
                  <option value="CONTRACT">Contract Update</option>
                  <option value="CORRECTION">Correction</option>
                </select>
              </label>
            </div>
          </fieldset>
          <fieldset class="form-section">
            <legend class="section-title">Approval Controls</legend>
            <div class="check-row">
              <label class="check-control"><input v-model="form.approvalRequired" type="checkbox" /> Approval required</label>
              <label class="check-control"><input v-model="form.blockUntilApproved" type="checkbox" /> Block until approved</label>
              <label class="check-control"><input v-model="form.notifyOwner" type="checkbox" /> Notify record owner</label>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Notes'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">References</legend>
            <div class="field-grid">
              <label class="field span-2">
                <span class="field-label">Internal Reference</span>
                <input v-model.trim="form.internalReference" class="control" placeholder="Contract, campaign, or ticket reference" />
              </label>
              <label class="field">
                <span class="field-label">Record Owner</span>
                <input v-model.trim="form.recordOwner" class="control" placeholder="Pricing owner" />
              </label>
              <label class="field">
                <span class="field-label">Source</span>
                <select v-model="form.source" class="control">
                  <option value="MANUAL">Manual Entry</option>
                  <option value="CONTRACT">Contract</option>
                  <option value="CAMPAIGN">Campaign</option>
                  <option value="IMPORT">Data Import</option>
                </select>
              </label>
              <label class="field span-4">
                <span class="field-label">Notes</span>
                <textarea v-model.trim="form.notes" class="textarea-control" placeholder="Internal pricing notes"></textarea>
              </label>
            </div>
          </fieldset>
        </div>
      </section>

      <section class="list-panel" aria-labelledby="condition-list-title">
        <div class="list-toolbar">
          <div class="toolbar-left">
            <h2 id="condition-list-title" class="list-title">Condition Records</h2>
            <span class="record-count">{{ filteredRows.length }} of {{ rows.length }} records</span>
          </div>
          <div class="toolbar-right">
            <label class="search-box">
              <Search />
              <input v-model.trim="searchText" class="control" placeholder="Search record or object" aria-label="Search pricing conditions" />
            </label>
            <select v-model="typeFilter" class="control filter-control" aria-label="Filter by condition type">
              <option value="">All condition types</option>
              <option v-for="type in conditionTypes" :key="type" :value="type">{{ type }}</option>
            </select>
            <select v-model="statusFilter" class="control filter-control" aria-label="Filter by status">
              <option value="">All statuses</option>
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
            </select>
            <button class="icon-button" type="button" title="Reset filters" aria-label="Reset condition filters" @click="resetFilters">
              <RefreshLeft />
            </button>
          </div>
        </div>

        <div v-if="loading" class="loading-state">Loading pricing conditions...</div>
        <div v-else-if="error" class="error-state">{{ error }}</div>
        <div v-else-if="filteredRows.length === 0" class="empty-state">No condition records match the current filters.</div>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Record ID</th>
                <th>Cond. Type</th>
                <th>Name</th>
                <th>Material</th>
                <th>Customer</th>
                <th class="numeric">Value</th>
                <th>Valid From</th>
                <th>Valid To</th>
                <th>Status</th>
                <th aria-label="Actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in filteredRows"
                :key="row.condition_id"
                :class="{ selected: selectedConditionId === row.condition_id }"
                @click="loadCondition(row)"
              >
                <td class="mono">{{ row.condition_id }}</td>
                <td class="mono">{{ row.condition_type }}</td>
                <td>{{ row.condition_name }}</td>
                <td class="mono">{{ row.material_id || '*' }}</td>
                <td class="mono">{{ row.bp_id || '*' }}</td>
                <td class="numeric mono">{{ formatConditionValue(row) }}</td>
                <td>{{ row.valid_from || '-' }}</td>
                <td>{{ row.valid_to || '-' }}</td>
                <td><span class="status-tag" :class="statusClass(row.status)">{{ normalizedStatus(row.status) }}</span></td>
                <td>
                  <button class="icon-button" type="button" title="Load condition" :aria-label="`Load ${row.condition_id}`" @click.stop="loadCondition(row)">
                    <EditPen />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <footer class="action-bar">
        <div class="status-summary">
          <span class="status-dot"></span>
          <span>{{ selectedConditionId ? `Selected ${selectedConditionId}` : 'New condition' }} | {{ activeTab }}</span>
        </div>
        <div class="action-group">
          <button class="primary-button" type="button" @click="saveDraft(false)">
            <DocumentChecked />
            Save
          </button>
          <button class="secondary-button" type="button" @click="saveDraft(true)">
            <ArrowRight />
            Save &amp; Continue
          </button>
          <button class="quiet-button" type="button" @click="cancelChanges">
            <Close />
            Cancel
          </button>
        </div>
      </footer>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowRight, Close, Coin, DocumentChecked, EditPen, Plus, RefreshLeft, Search } from '@element-plus/icons-vue'
import axios from 'axios'
import MainLayout from '@/layout/MainLayout.vue'

interface PricingCondition {
  condition_id: string
  condition_type: string
  condition_name: string
  material_id?: string | null
  bp_id?: string | null
  amount?: number | string | null
  rate?: number | string | null
  currency?: string | null
  valid_from?: string | null
  valid_to?: string | null
  status?: string | null
}

const tabs = ['Condition Record', 'Scope', 'Scales', 'Validity', 'Calculation', 'Approval', 'Notes']
const activeTab = ref('Condition Record')
const rows = ref<PricingCondition[]>([])
const selectedConditionId = ref('')
const loading = ref(true)
const error = ref('')
const searchText = ref('')
const typeFilter = ref('')
const statusFilter = ref('')

function createInitialForm() {
  return {
    conditionId: '',
    conditionType: 'PR00',
    application: 'V',
    status: 'ACTIVE',
    conditionName: '',
    calculationType: 'AMOUNT',
    conditionCategory: 'PRICE',
    amount: '',
    rate: '',
    currency: 'CNY',
    pricingUnit: '1',
    unitOfMeasure: 'EA',
    conditionUsage: 'A',
    manualEntry: true,
    headerCondition: false,
    itemCondition: true,
    salesOrg: '*',
    distributionChannel: '*',
    division: '*',
    priceList: '*',
    materialId: '*',
    businessPartnerId: '*',
    customerGroup: '*',
    materialPricingGroup: '*',
    scaleBasis: 'QUANTITY',
    scaleType: 'FROM',
    scaleUom: 'EA',
    scale1Qty: '',
    scale1Amount: '',
    scale1Rate: '',
    scale2Qty: '',
    scale2Amount: '',
    scale2Rate: '',
    scale3Qty: '',
    scale3Amount: '',
    scale3Rate: '',
    validFrom: '',
    validTo: '',
    releaseStatus: 'RELEASED',
    pricingDateCategory: 'ORDER',
    exclusive: false,
    autoExtend: false,
    deletionFlag: false,
    pricingProcedure: 'RVAA01',
    accessSequence: 'PR00',
    roundingRule: 'COMMERCIAL',
    decimalPlaces: '2',
    minimumValue: '',
    maximumValue: '',
    statistical: false,
    accrual: false,
    groupCondition: false,
    approvalStatus: 'NOT_REQUIRED',
    approverGroup: 'PRICING',
    releaseCode: '',
    changeReason: 'NEW',
    approvalRequired: false,
    blockUntilApproved: false,
    notifyOwner: true,
    internalReference: '',
    recordOwner: '',
    source: 'MANUAL',
    notes: '',
  }
}

const form = reactive(createInitialForm())

const conditionTypes = computed(() => {
  return Array.from(new Set(rows.value.map((row) => row.condition_type).filter(Boolean))).sort()
})

const filteredRows = computed(() => {
  const query = searchText.value.toLowerCase()
  return rows.value.filter((row) => {
    const matchesSearch = !query || [row.condition_id, row.condition_name, row.material_id, row.bp_id]
      .some((value) => String(value || '').toLowerCase().includes(query))
    const matchesType = !typeFilter.value || row.condition_type === typeFilter.value
    const matchesStatus = !statusFilter.value || normalizedStatus(row.status) === statusFilter.value
    return matchesSearch && matchesType && matchesStatus
  })
})

function normalizedStatus(status?: string | null) {
  return String(status || 'ACTIVE').toUpperCase()
}

function statusClass(status?: string | null) {
  const value = normalizedStatus(status)
  if (value === 'ACTIVE') return 'status-active'
  if (value === 'DRAFT') return 'status-draft'
  return 'status-inactive'
}

function hasValue(value: unknown) {
  return value !== null && value !== undefined && value !== ''
}

function formatConditionValue(row: PricingCondition) {
  if (hasValue(row.amount)) {
    const parsed = Number(row.amount)
    return `${Number.isFinite(parsed) ? parsed.toFixed(2) : row.amount} ${row.currency || ''}`.trim()
  }
  if (hasValue(row.rate)) {
    const parsed = Number(row.rate)
    return `${Number.isFinite(parsed) ? parsed.toFixed(2) : row.rate}%`
  }
  return '-'
}

function loadCondition(row: PricingCondition) {
  selectedConditionId.value = row.condition_id
  Object.assign(form, createInitialForm(), {
    conditionId: row.condition_id,
    conditionType: row.condition_type,
    conditionName: row.condition_name,
    materialId: row.material_id || '*',
    businessPartnerId: row.bp_id || '*',
    amount: row.amount == null ? '' : String(row.amount),
    rate: row.rate == null ? '' : String(row.rate),
    currency: row.currency || 'CNY',
    validFrom: row.valid_from || '',
    validTo: row.valid_to || '',
    status: normalizedStatus(row.status),
    calculationType: hasValue(row.rate) && !hasValue(row.amount) ? 'PERCENT' : 'AMOUNT',
  })
  activeTab.value = 'Condition Record'
}

function startNewCondition() {
  selectedConditionId.value = ''
  Object.assign(form, createInitialForm())
  activeTab.value = 'Condition Record'
}

function cancelChanges() {
  if (selectedConditionId.value) {
    const selected = rows.value.find((row) => row.condition_id === selectedConditionId.value)
    if (selected) loadCondition(selected)
  } else {
    Object.assign(form, createInitialForm())
    activeTab.value = 'Condition Record'
  }
  ElMessage({ message: 'Local changes cleared.', type: 'info', customClass: 'hakimi-toast-bottom' })
}

function resetFilters() {
  searchText.value = ''
  typeFilter.value = ''
  statusFilter.value = ''
}

function saveDraft(continueEditing: boolean) {
  if (!form.conditionId || !form.conditionType || !form.conditionName) {
    activeTab.value = 'Condition Record'
    ElMessage({ message: 'Record ID, Condition Type, and Condition Name are required.', type: 'warning', customClass: 'hakimi-toast-bottom' })
    return
  }
  ElMessage({
    message: continueEditing ? 'Pricing draft checked locally. Continue editing.' : 'Pricing draft checked locally. Server save is not enabled.',
    type: 'success',
    customClass: 'hakimi-toast-bottom',
  })
}

async function fetchConditions() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/api/v1/master/materials/pricing-conditions', { params: { page_size: 100 } })
    rows.value = response.data?.data?.items || []
  } catch (requestError: any) {
    error.value = requestError.response?.data?.detail || requestError.message || 'Failed to load pricing conditions'
  } finally {
    loading.value = false
  }
}

onMounted(fetchConditions)
</script>

<style scoped src="./master-workspace.css"></style>
