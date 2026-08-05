<template>
  <MainLayout>
    <div class="workspace-page">
      <header class="page-header">
        <div class="header-identity">
          <span class="header-icon"><OfficeBuilding /></span>
          <div>
            <h1 class="page-title">Sales Organization</h1>
            <p class="page-subtitle">Sales areas, channels, divisions, offices, shipping, and billing defaults</p>
          </div>
        </div>
        <div class="header-actions">
          <span class="mode-pill">{{ selectedOrganizationKey ? 'Display / Edit' : 'Create' }}</span>
          <button class="secondary-button" type="button" @click="startNewOrganization">
            <Plus />
            New Sales Area
          </button>
        </div>
      </header>

      <section class="workspace-panel record-header" aria-label="Sales organization key fields">
        <div class="key-grid">
          <label class="field">
            <span class="field-label required">Sales Organization ID</span>
            <input v-model.trim="form.salesOrgId" class="control mono" placeholder="e.g. 1000" />
          </label>
          <label class="field">
            <span class="field-label required">Distribution Channel</span>
            <select v-model="form.distributionChannel" class="control">
              <option value="10">10 - Direct Sales</option>
              <option value="20">20 - Wholesale</option>
              <option value="30">30 - Online</option>
              <option value="40">40 - Partner Sales</option>
            </select>
          </label>
          <label class="field">
            <span class="field-label required">Division</span>
            <select v-model="form.division" class="control">
              <option value="01">01 - Standard Products</option>
              <option value="02">02 - Services</option>
              <option value="03">03 - Spare Parts</option>
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

      <section class="workspace-panel tab-shell" aria-label="Sales organization details">
        <nav class="tab-bar" aria-label="Sales organization data views">
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

        <div v-show="activeTab === 'Basic Data'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Organization Data</legend>
            <div class="field-grid">
              <label class="field span-2">
                <span class="field-label required">Description</span>
                <input v-model.trim="form.description" class="control" placeholder="Sales organization description" />
              </label>
              <label class="field">
                <span class="field-label">Company Code</span>
                <select v-model="form.companyCode" class="control">
                  <option value="1000">1000 - Hakimi China</option>
                  <option value="2000">2000 - Hakimi International</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Business Area</span>
                <select v-model="form.businessArea" class="control">
                  <option value="1000">1000 - Domestic Operations</option>
                  <option value="2000">2000 - International Operations</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Country</span>
                <select v-model="form.country" class="control">
                  <option value="CN">CN - China</option>
                  <option value="US">US - United States</option>
                  <option value="DE">DE - Germany</option>
                  <option value="SG">SG - Singapore</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Currency</span>
                <select v-model="form.currency" class="control">
                  <option>CNY</option>
                  <option>USD</option>
                  <option>EUR</option>
                  <option>SGD</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Language</span>
                <select v-model="form.language" class="control">
                  <option value="ZH">ZH - Chinese</option>
                  <option value="EN">EN - English</option>
                  <option value="DE">DE - German</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Time Zone</span>
                <select v-model="form.timeZone" class="control">
                  <option value="Asia/Shanghai">Asia/Shanghai</option>
                  <option value="America/New_York">America/New_York</option>
                  <option value="Europe/Berlin">Europe/Berlin</option>
                </select>
              </label>
            </div>
          </fieldset>
          <fieldset class="form-section">
            <legend class="section-title">Address</legend>
            <div class="field-grid">
              <label class="field span-2">
                <span class="field-label">Street</span>
                <input v-model.trim="form.street" class="control" placeholder="Street and building" />
              </label>
              <label class="field">
                <span class="field-label">City</span>
                <input v-model.trim="form.city" class="control" placeholder="City" />
              </label>
              <label class="field">
                <span class="field-label">Postal Code</span>
                <input v-model.trim="form.postalCode" class="control mono" placeholder="Postal code" />
              </label>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Channels'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Channel Definition</legend>
            <div class="field-grid">
              <label class="field span-2">
                <span class="field-label">Channel Description</span>
                <input v-model.trim="form.channelDescription" class="control" placeholder="Distribution channel description" />
              </label>
              <label class="field">
                <span class="field-label">Channel Type</span>
                <select v-model="form.channelType" class="control">
                  <option value="DIRECT">Direct</option>
                  <option value="INDIRECT">Indirect</option>
                  <option value="DIGITAL">Digital</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Default Warehouse</span>
                <select v-model="form.defaultWarehouse" class="control">
                  <option value="WH01">WH01 - Main Warehouse</option>
                  <option value="WH02">WH02 - East Warehouse</option>
                  <option value="WH03">WH03 - Export Warehouse</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Customer Determination</span>
                <select v-model="form.customerDetermination" class="control">
                  <option value="STANDARD">Standard</option>
                  <option value="PARTNER">Partner Hierarchy</option>
                  <option value="ONLINE">Online Account</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Order Combination</span>
                <select v-model="form.orderCombination" class="control">
                  <option value="ALLOW">Allowed</option>
                  <option value="SAME_DAY">Same Day Only</option>
                  <option value="BLOCK">Not Allowed</option>
                </select>
              </label>
              <div class="field span-2">
                <span class="field-label">Allowed Processes</span>
                <div class="check-row">
                  <label class="check-control"><input v-model="form.standardOrders" type="checkbox" /> Standard orders</label>
                  <label class="check-control"><input v-model="form.returns" type="checkbox" /> Returns</label>
                  <label class="check-control"><input v-model="form.freeGoods" type="checkbox" /> Free goods</label>
                </div>
              </div>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Divisions'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Division Assignment</legend>
            <div class="field-grid">
              <label class="field span-2">
                <span class="field-label">Division Description</span>
                <input v-model.trim="form.divisionDescription" class="control" placeholder="Division description" />
              </label>
              <label class="field">
                <span class="field-label">Reference Division</span>
                <select v-model="form.referenceDivision" class="control">
                  <option value="01">01 - Standard Products</option>
                  <option value="02">02 - Services</option>
                  <option value="03">03 - Spare Parts</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Product Hierarchy</span>
                <input v-model.trim="form.productHierarchy" class="control mono" placeholder="Hierarchy root" />
              </label>
              <label class="field">
                <span class="field-label">Common Distribution Channel</span>
                <select v-model="form.commonChannel" class="control">
                  <option value="10">10 - Direct Sales</option>
                  <option value="20">20 - Wholesale</option>
                  <option value="30">30 - Online</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Material Division Check</span>
                <select v-model="form.materialDivisionCheck" class="control">
                  <option value="ERROR">Error</option>
                  <option value="WARNING">Warning</option>
                  <option value="NONE">No Check</option>
                </select>
              </label>
              <div class="field span-2">
                <span class="field-label">Shared Master Data</span>
                <div class="check-row">
                  <label class="check-control"><input v-model="form.commonCustomers" type="checkbox" /> Common customer master</label>
                  <label class="check-control"><input v-model="form.commonMaterials" type="checkbox" /> Common material master</label>
                  <label class="check-control"><input v-model="form.commonConditions" type="checkbox" /> Common conditions</label>
                </div>
              </div>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Offices & Groups'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Responsibility</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Sales Office</span>
                <select v-model="form.salesOffice" class="control">
                  <option value="1000">1000 - Headquarters</option>
                  <option value="1100">1100 - East Region</option>
                  <option value="1200">1200 - South Region</option>
                  <option value="2000">2000 - International</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Sales Group</span>
                <select v-model="form.salesGroup" class="control">
                  <option value="001">001 - General Sales</option>
                  <option value="002">002 - Key Accounts</option>
                  <option value="003">003 - Channel Sales</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Responsible Manager</span>
                <input v-model.trim="form.responsibleManager" class="control" placeholder="Manager name" />
              </label>
              <label class="field">
                <span class="field-label">Internal Contact</span>
                <input v-model.trim="form.internalContact" class="control" placeholder="Contact person" />
              </label>
            </div>
          </fieldset>
          <fieldset class="form-section">
            <legend class="section-title">Contact Details</legend>
            <div class="field-grid cols-2">
              <label class="field">
                <span class="field-label">Email</span>
                <input v-model.trim="form.email" class="control" type="email" placeholder="sales@example.com" />
              </label>
              <label class="field">
                <span class="field-label">Phone</span>
                <input v-model.trim="form.phone" class="control" type="tel" placeholder="Phone number" />
              </label>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Shipping'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Delivery Setup</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Delivering Plant</span>
                <select v-model="form.deliveringPlant" class="control">
                  <option value="1000">1000 - Main Plant</option>
                  <option value="1100">1100 - East Plant</option>
                  <option value="1200">1200 - South Plant</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Shipping Point</span>
                <select v-model="form.shippingPoint" class="control">
                  <option value="1000">1000 - Main Shipping</option>
                  <option value="1100">1100 - Express Shipping</option>
                  <option value="1200">1200 - Export Shipping</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Shipping Condition</span>
                <select v-model="form.shippingCondition" class="control">
                  <option value="01">01 - Standard</option>
                  <option value="02">02 - Express</option>
                  <option value="03">03 - Customer Pickup</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Default Route</span>
                <select v-model="form.defaultRoute" class="control">
                  <option value="CN01">CN01 - Domestic Standard</option>
                  <option value="CN02">CN02 - Domestic Express</option>
                  <option value="EX01">EX01 - Export Air</option>
                  <option value="EX02">EX02 - Export Sea</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Delivery Block</span>
                <select v-model="form.deliveryBlock" class="control">
                  <option value="">No Default Block</option>
                  <option value="01">01 - Credit Review</option>
                  <option value="02">02 - Export Check</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Lead Time</span>
                <div class="input-affix">
                  <input v-model="form.deliveryLeadTime" class="control" type="number" min="0" step="1" />
                  <span class="affix">Days</span>
                </div>
              </label>
              <div class="field span-2">
                <span class="field-label">Delivery Controls</span>
                <div class="check-row">
                  <label class="check-control"><input v-model="form.partialDelivery" type="checkbox" /> Partial delivery allowed</label>
                  <label class="check-control"><input v-model="form.completeDelivery" type="checkbox" /> Complete delivery required</label>
                </div>
              </div>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Billing'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Pricing and Billing</legend>
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
                <span class="field-label">Billing Type</span>
                <select v-model="form.billingType" class="control">
                  <option value="F2">F2 - Invoice</option>
                  <option value="G2">G2 - Credit Memo</option>
                  <option value="L2">L2 - Debit Memo</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Payment Terms</span>
                <select v-model="form.paymentTerms" class="control">
                  <option value="0001">0001 - Immediate</option>
                  <option value="0002">0002 - Net 30 Days</option>
                  <option value="0003">0003 - Net 60 Days</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Incoterms</span>
                <select v-model="form.incoterms" class="control">
                  <option value="EXW">EXW - Ex Works</option>
                  <option value="FOB">FOB - Free on Board</option>
                  <option value="CIF">CIF - Cost, Insurance and Freight</option>
                  <option value="DDP">DDP - Delivered Duty Paid</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Credit Control Area</span>
                <select v-model="form.creditControlArea" class="control">
                  <option value="1000">1000 - Domestic Credit</option>
                  <option value="2000">2000 - Export Credit</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Tax Jurisdiction</span>
                <input v-model.trim="form.taxJurisdiction" class="control mono" placeholder="Tax jurisdiction code" />
              </label>
              <div class="field span-2">
                <span class="field-label">Billing Controls</span>
                <div class="check-row">
                  <label class="check-control"><input v-model="form.orderRelatedBilling" type="checkbox" /> Order-related billing</label>
                  <label class="check-control"><input v-model="form.invoiceList" type="checkbox" /> Invoice list enabled</label>
                </div>
              </div>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Defaults'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Document Defaults</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Order Type</span>
                <select v-model="form.orderType" class="control">
                  <option value="OR">OR - Standard Order</option>
                  <option value="RE">RE - Returns</option>
                  <option value="ZOR">ZOR - Custom Order</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Delivery Type</span>
                <select v-model="form.deliveryType" class="control">
                  <option value="LF">LF - Outbound Delivery</option>
                  <option value="LR">LR - Returns Delivery</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Sales Unit</span>
                <select v-model="form.salesUnit" class="control">
                  <option>EA</option>
                  <option>BOX</option>
                  <option>PAL</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Customer Group</span>
                <select v-model="form.customerGroup" class="control">
                  <option value="01">01 - Retail</option>
                  <option value="02">02 - Wholesale</option>
                  <option value="03">03 - Key Accounts</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Sales District</span>
                <select v-model="form.salesDistrict" class="control">
                  <option value="CN-N">CN-N - North China</option>
                  <option value="CN-E">CN-E - East China</option>
                  <option value="CN-S">CN-S - South China</option>
                  <option value="INTL">INTL - International</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Output Procedure</span>
                <select v-model="form.outputProcedure" class="control">
                  <option value="V10000">V10000 - Sales Documents</option>
                  <option value="V20000">V20000 - Deliveries</option>
                  <option value="V30000">V30000 - Billing</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Default Partner Procedure</span>
                <select v-model="form.partnerProcedure" class="control">
                  <option value="AG">AG - Sold-to Party</option>
                  <option value="WE">WE - Ship-to Party</option>
                  <option value="RE">RE - Bill-to Party</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Statistics Group</span>
                <select v-model="form.statisticsGroup" class="control">
                  <option value="1">1 - Relevant</option>
                  <option value="0">0 - Not Relevant</option>
                </select>
              </label>
            </div>
          </fieldset>
        </div>
      </section>

      <section class="list-panel" aria-labelledby="organization-list-title">
        <div class="list-toolbar">
          <div class="toolbar-left">
            <h2 id="organization-list-title" class="list-title">Sales Areas</h2>
            <span class="record-count">{{ filteredRows.length }} of {{ rows.length }} records</span>
          </div>
          <div class="toolbar-right">
            <label class="search-box">
              <Search />
              <input v-model.trim="searchText" class="control" placeholder="Search organization" aria-label="Search sales organizations" />
            </label>
            <select v-model="channelFilter" class="control filter-control" aria-label="Filter by channel">
              <option value="">All channels</option>
              <option v-for="channel in channelOptions" :key="channel" :value="channel">Channel {{ channel }}</option>
            </select>
            <select v-model="statusFilter" class="control filter-control" aria-label="Filter by status">
              <option value="">All statuses</option>
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
            </select>
            <button class="icon-button" type="button" title="Reset filters" aria-label="Reset sales organization filters" @click="resetFilters">
              <RefreshLeft />
            </button>
          </div>
        </div>

        <div v-if="loading" class="loading-state">Loading sales organizations...</div>
        <div v-else-if="error" class="error-state">{{ error }}</div>
        <div v-else-if="filteredRows.length === 0" class="empty-state">No sales areas match the current filters.</div>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Sales Org</th>
                <th>Description</th>
                <th>Dist. Channel</th>
                <th>Division</th>
                <th>Currency</th>
                <th>Country</th>
                <th>Status</th>
                <th aria-label="Actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in filteredRows"
                :key="organizationKey(row)"
                :class="{ selected: selectedOrganizationKey === organizationKey(row) }"
                @click="loadOrganization(row)"
              >
                <td class="mono">{{ row.sales_org_id }}</td>
                <td>{{ row.description }}</td>
                <td class="mono">{{ row.distribution_channel }}</td>
                <td class="mono">{{ row.division }}</td>
                <td>{{ row.currency || 'CNY' }}</td>
                <td>{{ row.country || 'CN' }}</td>
                <td><span class="status-tag" :class="statusClass(row.status)">{{ normalizedStatus(row.status) }}</span></td>
                <td>
                  <button class="icon-button" type="button" title="Load sales area" :aria-label="`Load ${organizationKey(row)}`" @click.stop="loadOrganization(row)">
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
          <span>{{ selectedOrganizationKey ? `Selected ${selectedOrganizationKey}` : 'New sales area' }} | {{ activeTab }}</span>
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
import { ArrowRight, Close, DocumentChecked, EditPen, OfficeBuilding, Plus, RefreshLeft, Search } from '@element-plus/icons-vue'
import axios from 'axios'
import MainLayout from '@/layout/MainLayout.vue'

interface SalesOrganization {
  sales_org_id: string
  description: string
  distribution_channel: string
  division: string
  currency?: string | null
  country?: string | null
  status?: string | null
}

const tabs = ['Basic Data', 'Channels', 'Divisions', 'Offices & Groups', 'Shipping', 'Billing', 'Defaults']
const activeTab = ref('Basic Data')
const rows = ref<SalesOrganization[]>([])
const selectedOrganizationKey = ref('')
const loading = ref(true)
const error = ref('')
const searchText = ref('')
const channelFilter = ref('')
const statusFilter = ref('')

function createInitialForm() {
  return {
    salesOrgId: '',
    distributionChannel: '10',
    division: '01',
    status: 'ACTIVE',
    description: '',
    companyCode: '1000',
    businessArea: '1000',
    country: 'CN',
    currency: 'CNY',
    language: 'ZH',
    timeZone: 'Asia/Shanghai',
    street: '',
    city: '',
    postalCode: '',
    channelDescription: 'Direct Sales',
    channelType: 'DIRECT',
    defaultWarehouse: 'WH01',
    customerDetermination: 'STANDARD',
    orderCombination: 'ALLOW',
    standardOrders: true,
    returns: true,
    freeGoods: false,
    divisionDescription: 'Standard Products',
    referenceDivision: '01',
    productHierarchy: '',
    commonChannel: '10',
    materialDivisionCheck: 'WARNING',
    commonCustomers: true,
    commonMaterials: true,
    commonConditions: true,
    salesOffice: '1000',
    salesGroup: '001',
    responsibleManager: '',
    internalContact: '',
    email: '',
    phone: '',
    deliveringPlant: '1000',
    shippingPoint: '1000',
    shippingCondition: '01',
    defaultRoute: 'CN01',
    deliveryBlock: '',
    deliveryLeadTime: '2',
    partialDelivery: true,
    completeDelivery: false,
    pricingProcedure: 'RVAA01',
    billingType: 'F2',
    paymentTerms: '0002',
    incoterms: 'EXW',
    creditControlArea: '1000',
    taxJurisdiction: '',
    orderRelatedBilling: false,
    invoiceList: false,
    orderType: 'OR',
    deliveryType: 'LF',
    salesUnit: 'EA',
    customerGroup: '01',
    salesDistrict: 'CN-E',
    outputProcedure: 'V10000',
    partnerProcedure: 'AG',
    statisticsGroup: '1',
  }
}

const form = reactive(createInitialForm())

const channelOptions = computed(() => {
  return Array.from(new Set(rows.value.map((row) => row.distribution_channel).filter(Boolean))).sort()
})

const filteredRows = computed(() => {
  const query = searchText.value.toLowerCase()
  return rows.value.filter((row) => {
    const matchesSearch = !query || [row.sales_org_id, row.description, row.distribution_channel, row.division]
      .some((value) => String(value || '').toLowerCase().includes(query))
    const matchesChannel = !channelFilter.value || row.distribution_channel === channelFilter.value
    const matchesStatus = !statusFilter.value || normalizedStatus(row.status) === statusFilter.value
    return matchesSearch && matchesChannel && matchesStatus
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

function organizationKey(row: SalesOrganization) {
  return `${row.sales_org_id}/${row.distribution_channel}/${row.division}`
}

function loadOrganization(row: SalesOrganization) {
  selectedOrganizationKey.value = organizationKey(row)
  Object.assign(form, createInitialForm(), {
    salesOrgId: row.sales_org_id,
    description: row.description,
    distributionChannel: row.distribution_channel,
    division: row.division,
    currency: row.currency || 'CNY',
    country: row.country || 'CN',
    status: normalizedStatus(row.status),
    channelDescription: `Channel ${row.distribution_channel}`,
    divisionDescription: `Division ${row.division}`,
  })
  activeTab.value = 'Basic Data'
}

function startNewOrganization() {
  selectedOrganizationKey.value = ''
  Object.assign(form, createInitialForm())
  activeTab.value = 'Basic Data'
}

function cancelChanges() {
  if (selectedOrganizationKey.value) {
    const selected = rows.value.find((row) => organizationKey(row) === selectedOrganizationKey.value)
    if (selected) loadOrganization(selected)
  } else {
    Object.assign(form, createInitialForm())
    activeTab.value = 'Basic Data'
  }
  ElMessage({ message: 'Local changes cleared.', type: 'info', customClass: 'hakimi-toast-bottom' })
}

function resetFilters() {
  searchText.value = ''
  channelFilter.value = ''
  statusFilter.value = ''
}

function saveDraft(continueEditing: boolean) {
  if (!form.salesOrgId || !form.distributionChannel || !form.division || !form.description) {
    activeTab.value = 'Basic Data'
    ElMessage({ message: 'Sales Organization ID, channel, division, and description are required.', type: 'warning', customClass: 'hakimi-toast-bottom' })
    return
  }
  ElMessage({
    message: continueEditing ? 'Sales area draft checked locally. Continue editing.' : 'Sales area draft checked locally. Server save is not enabled.',
    type: 'success',
    customClass: 'hakimi-toast-bottom',
  })
}

async function fetchOrganizations() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/api/v1/master/materials/sales-organizations', { params: { page_size: 50 } })
    rows.value = response.data?.data?.items || []
  } catch (requestError: any) {
    error.value = requestError.response?.data?.detail || requestError.message || 'Failed to load sales organizations'
  } finally {
    loading.value = false
  }
}

onMounted(fetchOrganizations)
</script>

<style scoped src="./master-workspace.css"></style>
