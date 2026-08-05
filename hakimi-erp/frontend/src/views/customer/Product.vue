<template>
  <MainLayout>
    <div class="workspace-page">
      <header class="page-header">
        <div class="header-identity">
          <span class="header-icon"><Box /></span>
          <div>
            <h1 class="page-title">Product Master</h1>
            <p class="page-subtitle">Product identity, sales attributes, pricing, availability, and logistics data</p>
          </div>
        </div>
        <div class="header-actions">
          <span class="mode-pill">{{ selectedProductId ? 'Display / Edit' : 'Create' }}</span>
          <button class="secondary-button" type="button" @click="startNewProduct">
            <Plus />
            New Product
          </button>
        </div>
      </header>

      <section class="workspace-panel record-header" aria-label="Product key fields">
        <div class="key-grid">
          <label class="field">
            <span class="field-label required">Product ID</span>
            <input v-model.trim="form.productId" class="control mono" placeholder="e.g. MAT-10001" />
          </label>
          <label class="field">
            <span class="field-label required">Product Type</span>
            <select v-model="form.productType" class="control">
              <option>FERT - Finished Product</option>
              <option>HAWA - Trading Goods</option>
              <option>HALB - Semi-Finished Product</option>
              <option>DIEN - Service</option>
            </select>
          </label>
          <label class="field">
            <span class="field-label required">Base UoM</span>
            <select v-model="form.baseUom" class="control">
              <option value="EA">EA - Each</option>
              <option value="KG">KG - Kilogram</option>
              <option value="L">L - Liter</option>
              <option value="M">M - Meter</option>
              <option value="BOX">BOX - Box</option>
              <option value="PC">PC - Piece</option>
              <option value="SET">SET - Set</option>
              <option value="BAG">BAG - Bag</option>
              <option value="BARREL">BARREL - Barrel</option>
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

      <section class="workspace-panel tab-shell" aria-label="Product details">
        <nav class="tab-bar" aria-label="Product data views">
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
            <legend class="section-title">General Data</legend>
            <div class="field-grid">
              <label class="field span-2">
                <span class="field-label required">Product Name</span>
                <input v-model.trim="form.productName" class="control" placeholder="Product short description" />
              </label>
              <label class="field">
                <span class="field-label">Category</span>
                <select v-model="form.category" class="control">
                  <option value="">Select category</option>
                  <option>Electronics</option>
                  <option>Mechanical</option>
                  <option>Consumables</option>
                  <option>Services</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Item Group</span>
                <select v-model="form.itemGroup" class="control">
                  <option value="">Select item group</option>
                  <option value="NORM">NORM - Standard Item</option>
                  <option value="SERV">SERV - Service Item</option>
                  <option value="FREE">FREE - Free of Charge</option>
                </select>
              </label>
              <label class="field span-2">
                <span class="field-label">Search Term</span>
                <input v-model.trim="form.searchTerm" class="control" placeholder="Catalog search keyword" />
              </label>
              <label class="field">
                <span class="field-label">Brand</span>
                <input v-model.trim="form.brand" class="control" placeholder="Brand or manufacturer" />
              </label>
              <label class="field">
                <span class="field-label">EAN / GTIN</span>
                <input v-model.trim="form.ean" class="control mono" placeholder="Barcode number" />
              </label>
            </div>
          </fieldset>
          <fieldset class="form-section">
            <legend class="section-title">Description</legend>
            <label class="field">
              <span class="field-label">Long Description</span>
              <textarea v-model.trim="form.description" class="textarea-control" placeholder="Product description"></textarea>
            </label>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Sales'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Sales Area</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Sales Organization</span>
                <select v-model="form.salesOrg" class="control">
                  <option value="1000">1000 - Domestic Sales</option>
                  <option value="2000">2000 - Export Sales</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Distribution Channel</span>
                <select v-model="form.distributionChannel" class="control">
                  <option value="10">10 - Direct Sales</option>
                  <option value="20">20 - Wholesale</option>
                  <option value="30">30 - Online</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Division</span>
                <select v-model="form.division" class="control">
                  <option value="00">00 - Cross Division</option>
                  <option value="10">10 - Standard Products</option>
                  <option value="20">20 - Services</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Item Category Group</span>
                <select v-model="form.itemCategoryGroup" class="control">
                  <option value="NORM">NORM - Standard Item</option>
                  <option value="SERV">SERV - Service</option>
                  <option value="LEIS">LEIS - No Delivery</option>
                </select>
              </label>
            </div>
          </fieldset>
          <fieldset class="form-section">
            <legend class="section-title">Order and Delivery</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Sales Unit</span>
                <select v-model="form.salesUnit" class="control">
                  <option value="EA">EA - Each</option>
                  <option value="BOX">BOX - Box</option>
                  <option value="PAL">PAL - Pallet</option>
                  <option value="PC">PC - Piece</option>
                  <option value="SET">SET - Set</option>
                  <option value="BAG">BAG - Bag</option>
                  <option value="BARREL">BARREL - Barrel</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Minimum Order Qty.</span>
                <input v-model="form.minimumOrderQty" class="control" type="number" min="0" step="1" />
              </label>
              <label class="field">
                <span class="field-label">Delivering Plant</span>
                <select v-model="form.deliveringPlant" class="control">
                  <option value="1000">1000 - Main Plant</option>
                  <option value="1100">1100 - East Plant</option>
                  <option value="1200">1200 - South Plant</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Tax Classification</span>
                <select v-model="form.taxClassification" class="control">
                  <option value="1">1 - Full Tax</option>
                  <option value="0">0 - Tax Exempt</option>
                </select>
              </label>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Pricing'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Price Reference</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Standard Price</span>
                <div class="input-affix">
                  <input v-model="form.standardPrice" class="control" type="number" min="0" step="0.01" />
                  <span class="affix">{{ form.currency }}</span>
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
                <span class="field-label">Price Unit</span>
                <input v-model="form.priceUnit" class="control" type="number" min="1" step="1" />
              </label>
              <label class="field">
                <span class="field-label">Price List</span>
                <select v-model="form.priceList" class="control">
                  <option value="01">01 - Standard</option>
                  <option value="02">02 - Wholesale</option>
                  <option value="03">03 - Export</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Pricing Group</span>
                <select v-model="form.pricingGroup" class="control">
                  <option value="01">01 - Standard Products</option>
                  <option value="02">02 - Promotional Products</option>
                  <option value="03">03 - Services</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Tax Code</span>
                <select v-model="form.taxCode" class="control">
                  <option value="A1">A1 - Output Tax</option>
                  <option value="A0">A0 - Tax Exempt</option>
                </select>
              </label>
              <div class="field span-2">
                <span class="field-label">Pricing Controls</span>
                <div class="check-row">
                  <label class="check-control"><input v-model="form.allowDiscount" type="checkbox" /> Discount allowed</label>
                  <label class="check-control"><input v-model="form.manualPrice" type="checkbox" /> Manual price allowed</label>
                </div>
              </div>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Availability'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Availability Check</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Checking Group</span>
                <select v-model="form.checkingGroup" class="control">
                  <option value="01">01 - Daily Requirements</option>
                  <option value="02">02 - Individual Requirements</option>
                  <option value="KP">KP - No Check</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Availability Rule</span>
                <select v-model="form.availabilityRule" class="control">
                  <option value="ATP">ATP - Available to Promise</option>
                  <option value="STOCK">STOCK - Stock Only</option>
                  <option value="NONE">NONE - No Check</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Replenishment Lead Time</span>
                <div class="input-affix">
                  <input v-model="form.replenishmentLeadTime" class="control" type="number" min="0" step="1" />
                  <span class="affix">Days</span>
                </div>
              </label>
              <label class="field">
                <span class="field-label">Safety Stock</span>
                <input v-model="form.safetyStock" class="control" type="number" min="0" step="1" />
              </label>
              <label class="field">
                <span class="field-label">Backorder Policy</span>
                <select v-model="form.backorderPolicy" class="control">
                  <option value="ALLOW">Allow Backorders</option>
                  <option value="REVIEW">Manual Review</option>
                  <option value="BLOCK">Block Backorders</option>
                </select>
              </label>
              <div class="field span-2">
                <span class="field-label">Stock Controls</span>
                <div class="check-row">
                  <label class="check-control"><input v-model="form.negativeStock" type="checkbox" /> Negative stock allowed</label>
                  <label class="check-control"><input v-model="form.transferStock" type="checkbox" /> Include transfer stock</label>
                </div>
              </div>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Logistics'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Dimensions and Weight</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Gross Weight</span>
                <div class="input-affix">
                  <input v-model="form.grossWeight" class="control" type="number" min="0" step="0.001" />
                  <span class="affix">{{ form.weightUnit }}</span>
                </div>
              </label>
              <label class="field">
                <span class="field-label">Net Weight</span>
                <div class="input-affix">
                  <input v-model="form.netWeight" class="control" type="number" min="0" step="0.001" />
                  <span class="affix">{{ form.weightUnit }}</span>
                </div>
              </label>
              <label class="field">
                <span class="field-label">Weight Unit</span>
                <select v-model="form.weightUnit" class="control">
                  <option>KG</option>
                  <option>LB</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Volume</span>
                <div class="input-affix">
                  <input v-model="form.volume" class="control" type="number" min="0" step="0.001" />
                  <span class="affix">{{ form.volumeUnit }}</span>
                </div>
              </label>
            </div>
          </fieldset>
          <fieldset class="form-section">
            <legend class="section-title">Handling</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Volume Unit</span>
                <select v-model="form.volumeUnit" class="control">
                  <option>M3</option>
                  <option>L</option>
                  <option>FT3</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Transportation Group</span>
                <select v-model="form.transportationGroup" class="control">
                  <option value="0001">0001 - On Pallets</option>
                  <option value="0002">0002 - Liquid</option>
                  <option value="0003">0003 - Container</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Loading Group</span>
                <select v-model="form.loadingGroup" class="control">
                  <option value="0001">0001 - Crane</option>
                  <option value="0002">0002 - Forklift</option>
                  <option value="0003">0003 - Manual</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Storage Condition</span>
                <select v-model="form.storageCondition" class="control">
                  <option value="01">01 - Dry Storage</option>
                  <option value="02">02 - Refrigerated</option>
                  <option value="03">03 - Outdoor</option>
                </select>
              </label>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Classification'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Product Classification</legend>
            <div class="field-grid">
              <label class="field">
                <span class="field-label">Product Hierarchy</span>
                <input v-model.trim="form.productHierarchy" class="control mono" placeholder="e.g. 00101" />
              </label>
              <label class="field">
                <span class="field-label">Product Class</span>
                <select v-model="form.productClass" class="control">
                  <option value="STANDARD">Standard Product</option>
                  <option value="CONFIG">Configurable Product</option>
                  <option value="SERVICE">Service Product</option>
                </select>
              </label>
              <label class="field">
                <span class="field-label">Characteristic Profile</span>
                <input v-model.trim="form.characteristicProfile" class="control" placeholder="Profile ID" />
              </label>
              <label class="field">
                <span class="field-label">Serial Number Profile</span>
                <select v-model="form.serialProfile" class="control">
                  <option value="">No serial profile</option>
                  <option value="0001">0001 - Serial at Delivery</option>
                  <option value="0002">0002 - Serial at Receipt</option>
                </select>
              </label>
              <div class="field span-2">
                <span class="field-label">Traceability</span>
                <div class="check-row">
                  <label class="check-control"><input v-model="form.batchManagement" type="checkbox" /> Batch management</label>
                  <label class="check-control"><input v-model="form.configurationRequired" type="checkbox" /> Configuration required</label>
                </div>
              </div>
            </div>
          </fieldset>
        </div>

        <div v-show="activeTab === 'Media'" class="tab-content">
          <fieldset class="form-section">
            <legend class="section-title">Catalog Media</legend>
            <div class="field-grid">
              <label class="field span-2">
                <span class="field-label">Primary Image URL</span>
                <input v-model.trim="form.primaryImageUrl" class="control" type="url" placeholder="https://..." />
              </label>
              <label class="field span-2">
                <span class="field-label">Document Reference</span>
                <input v-model.trim="form.documentReference" class="control" placeholder="Datasheet or document ID" />
              </label>
              <label class="field span-2">
                <span class="field-label">Alternative Text</span>
                <input v-model.trim="form.alternativeText" class="control" placeholder="Accessible image description" />
              </label>
              <label class="field span-2">
                <span class="field-label">Catalog URL</span>
                <input v-model.trim="form.catalogUrl" class="control" type="url" placeholder="https://..." />
              </label>
            </div>
          </fieldset>
        </div>
      </section>

      <section class="list-panel" aria-labelledby="product-list-title">
        <div class="list-toolbar">
          <div class="toolbar-left">
            <h2 id="product-list-title" class="list-title">Product List</h2>
            <span class="record-count">{{ filteredProducts.length }} of {{ products.length }} records</span>
          </div>
          <div class="toolbar-right">
            <label class="search-box">
              <Search />
              <input v-model.trim="searchText" class="control" placeholder="Search ID or name" aria-label="Search products" />
            </label>
            <select v-model="categoryFilter" class="control filter-control" aria-label="Filter by category">
              <option value="">All categories</option>
              <option v-for="category in categoryOptions" :key="category" :value="category">{{ category }}</option>
            </select>
            <select v-model="statusFilter" class="control filter-control" aria-label="Filter by status">
              <option value="">All statuses</option>
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
            </select>
            <button class="icon-button" type="button" title="Reset filters" aria-label="Reset product filters" @click="resetFilters">
              <RefreshLeft />
            </button>
          </div>
        </div>

        <div v-if="loading" class="loading-state">Loading products...</div>
        <div v-else-if="error" class="error-state">{{ error }}</div>
        <div v-else-if="filteredProducts.length === 0" class="empty-state">No products match the current filters.</div>
        <div v-else class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Product ID</th>
                <th>Name</th>
                <th>Category</th>
                <th class="numeric">Unit Price</th>
                <th>UoM</th>
                <th class="numeric">Stock</th>
                <th>Status</th>
                <th aria-label="Actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="product in filteredProducts"
                :key="product.material_id"
                :class="{ selected: selectedProductId === product.material_id }"
                @click="loadProduct(product)"
              >
                <td class="mono">{{ product.material_id }}</td>
                <td>{{ product.material_name }}</td>
                <td>{{ product.category || '-' }}</td>
                <td class="numeric mono">{{ formatNumber(product.standard_price, 2) }}</td>
                <td>{{ product.base_unit }}</td>
                <td class="numeric mono">{{ formatNumber(product.stock_quantity, 3) }}</td>
                <td>
                  <span class="status-tag" :class="statusClass(product.status)">{{ normalizedStatus(product.status) }}</span>
                </td>
                <td>
                  <button class="icon-button" type="button" title="Load product" :aria-label="`Load ${product.material_id}`" @click.stop="loadProduct(product)">
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
          <span>{{ selectedProductId ? `Selected ${selectedProductId}` : 'New product' }} | {{ activeTab }}</span>
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
import { ArrowRight, Box, Close, DocumentChecked, EditPen, Plus, RefreshLeft, Search } from '@element-plus/icons-vue'
import axios from 'axios'
import MainLayout from '@/layout/MainLayout.vue'

interface Product {
  material_id: string
  material_name: string
  description?: string | null
  base_unit: string
  standard_price?: number | string | null
  weight?: number | string | null
  volume?: number | string | null
  search_term?: string | null
  category?: string | null
  stock_quantity?: number | string | null
  item_group?: string | null
  status?: string | null
}

const tabs = ['Basic Data', 'Sales', 'Pricing', 'Availability', 'Logistics', 'Classification', 'Media']
const activeTab = ref('Basic Data')
const products = ref<Product[]>([])
const selectedProductId = ref('')
const loading = ref(true)
const error = ref('')
const searchText = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')

function createInitialForm() {
  return {
    productId: '',
    productType: 'FERT - Finished Product',
    baseUom: 'EA',
    status: 'ACTIVE',
    productName: '',
    description: '',
    category: '',
    itemGroup: 'NORM',
    searchTerm: '',
    brand: '',
    ean: '',
    salesOrg: '1000',
    distributionChannel: '10',
    division: '00',
    itemCategoryGroup: 'NORM',
    salesUnit: 'EA',
    minimumOrderQty: '1',
    deliveringPlant: '1000',
    taxClassification: '1',
    standardPrice: '',
    currency: 'CNY',
    priceUnit: '1',
    priceList: '01',
    pricingGroup: '01',
    taxCode: 'A1',
    allowDiscount: true,
    manualPrice: false,
    checkingGroup: '01',
    availabilityRule: 'ATP',
    replenishmentLeadTime: '0',
    safetyStock: '0',
    backorderPolicy: 'ALLOW',
    negativeStock: false,
    transferStock: true,
    grossWeight: '',
    netWeight: '',
    weightUnit: 'KG',
    volume: '',
    volumeUnit: 'M3',
    transportationGroup: '0001',
    loadingGroup: '0002',
    storageCondition: '01',
    productHierarchy: '',
    productClass: 'STANDARD',
    characteristicProfile: '',
    serialProfile: '',
    batchManagement: false,
    configurationRequired: false,
    primaryImageUrl: '',
    documentReference: '',
    alternativeText: '',
    catalogUrl: '',
  }
}

const form = reactive(createInitialForm())

const categoryOptions = computed(() => {
  return Array.from(new Set(products.value.map((product) => product.category).filter((value): value is string => Boolean(value)))).sort()
})

const filteredProducts = computed(() => {
  const query = searchText.value.toLowerCase()
  return products.value.filter((product) => {
    const matchesSearch = !query || [product.material_id, product.material_name, product.search_term]
      .some((value) => String(value || '').toLowerCase().includes(query))
    const matchesCategory = !categoryFilter.value || product.category === categoryFilter.value
    const matchesStatus = !statusFilter.value || normalizedStatus(product.status) === statusFilter.value
    return matchesSearch && matchesCategory && matchesStatus
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

function formatNumber(value: number | string | null | undefined, digits: number) {
  if (value === null || value === undefined || value === '') return '-'
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed.toFixed(digits) : String(value)
}

function loadProduct(product: Product) {
  selectedProductId.value = product.material_id
  Object.assign(form, createInitialForm(), {
    productId: product.material_id,
    productName: product.material_name,
    description: product.description || '',
    baseUom: product.base_unit || 'EA',
    status: normalizedStatus(product.status),
    standardPrice: product.standard_price == null ? '' : String(product.standard_price),
    netWeight: product.weight == null ? '' : String(product.weight),
    grossWeight: product.weight == null ? '' : String(product.weight),
    volume: product.volume == null ? '' : String(product.volume),
    searchTerm: product.search_term || '',
    category: product.category || '',
    itemGroup: product.item_group || 'NORM',
    salesUnit: product.base_unit || 'EA',
  })
  activeTab.value = 'Basic Data'
}

function startNewProduct() {
  selectedProductId.value = ''
  Object.assign(form, createInitialForm())
  activeTab.value = 'Basic Data'
}

function cancelChanges() {
  if (selectedProductId.value) {
    const selected = products.value.find((product) => product.material_id === selectedProductId.value)
    if (selected) loadProduct(selected)
  } else {
    Object.assign(form, createInitialForm())
    activeTab.value = 'Basic Data'
  }
  ElMessage({ message: 'Local changes cleared.', type: 'info', customClass: 'hakimi-toast-bottom' })
}

function resetFilters() {
  searchText.value = ''
  categoryFilter.value = ''
  statusFilter.value = ''
}

function saveDraft(continueEditing: boolean) {
  if (!form.productId || !form.productName) {
    activeTab.value = 'Basic Data'
    ElMessage({ message: 'Product ID and Product Name are required.', type: 'warning', customClass: 'hakimi-toast-bottom' })
    return
  }
  ElMessage({
    message: continueEditing ? 'Product draft checked locally. Continue editing.' : 'Product draft checked locally. Server save is not enabled.',
    type: 'success',
    customClass: 'hakimi-toast-bottom',
  })
}

async function fetchProducts() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/api/v1/master/materials/', { params: { page_size: 50 } })
    products.value = response.data?.data?.items || []
  } catch (requestError: any) {
    error.value = requestError.response?.data?.detail || requestError.message || 'Failed to load products'
  } finally {
    loading.value = false
  }
}

onMounted(fetchProducts)
</script>

<style scoped src="./master-workspace.css"></style>
