<template>
  <MainLayout>
    <div class="bp-page">
      <!-- Header -->
      <div class="page-header">
        <h2 class="page-title">Create Business Partner</h2>
        <button class="exit-btn" @click="handleExit">
          <svg viewBox="0 0 20 20" width="16" height="16">
            <path d="M6 6l8 8M14 6l-8 8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          Exit
        </button>
      </div>

      <!-- Top Form Row -->
      <div class="form-card">
        <div class="form-row form-row-3">
          <div class="form-group">
            <label class="form-label">Business Partner No.</label>
            <input type="text" class="form-input" v-model="form.bpId" placeholder="Auto-generated if empty" />
          </div>
          <div class="form-group">
            <label class="form-label">Grouping</label>
            <div class="input-with-f4"><select class="form-select" v-model="form.grouping">
              <option value="">Select grouping</option>
              <option value="EXT">External</option>
              <option value="INT">Internal</option>
            </select><button class="f4-trigger" @click="openF4('grouping')" title="F4 Search"><svg viewBox="0 0 20 20" width="14" height="14"><circle cx="9" cy="9" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M13 13l4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button></div>
          </div>
          <div class="form-group">
            <label class="form-label required">BP Role</label>
            <select class="form-select" v-model="form.bpRole">
              <option value="">Select role</option>
              <option value="FLCU01">Customer (FLCU01)</option>
              <option value="FLVN00">Vendor (FLVN00)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="form-card form-card-tabs">
        <div class="tab-bar">
          <button
            v-for="tab in tabs" :key="tab.key"
            class="tab-btn" :class="{ active: activeTab === tab.key }"
            @click="switchTab(tab.key)"
          >{{ tab.label }}</button>
        </div>

        <!-- Address Tab -->
        <div class="tab-content" v-show="activeTab === 'address'">
          <!-- Basic Information -->
          <fieldset class="fieldset-block">
            <legend class="block-title">Basic Information</legend>
            <div class="form-row form-row-4">
              <div class="form-group">
                <label class="form-label">Salutation</label>
                <select class="form-select" v-model="form.salutation">
                  <option value="">Select</option>
                  <option value="MR">Mr.</option>
                  <option value="MS">Ms.</option>
                  <option value="MRS">Mrs.</option>
                  <option value="DR">Dr.</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label required">Last Name</label>
                <input type="text" class="form-input" v-model="form.lastName" placeholder="Enter last name" />
              </div>
              <div class="form-group">
                <label class="form-label required">First Name</label>
                <input type="text" class="form-input" v-model="form.firstName" placeholder="Enter first name" />
              </div>
              <div class="form-group">
                <label class="form-label">Search Term</label>
                <input type="text" class="form-input" v-model="form.searchTerm" placeholder="Quick search keyword" />
              </div>
            </div>
          </fieldset>

          <!-- Standard Address -->
          <fieldset class="fieldset-block">
            <legend class="block-title">Standard Address</legend>
            <div class="form-row form-row-2">
              <div class="form-group">
                <label class="form-label">Street</label>
                <input type="text" class="form-input" v-model="form.street" placeholder="Street name" />
              </div>
              <div class="form-group">
                <label class="form-label">House No.</label>
                <input type="text" class="form-input" v-model="form.houseNumber" placeholder="House number" />
              </div>
            </div>
            <div class="form-row form-row-3">
              <div class="form-group">
                <label class="form-label required">Country / Region</label>
                <select class="form-select" v-model="form.country">
                  <option value="">Select country</option>
                  <option value="CN">China</option>
                  <option value="US">United States</option>
                  <option value="DE">Germany</option>
                  <option value="JP">Japan</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label required">City</label>
                <input type="text" class="form-input" v-model="form.city" placeholder="Enter city" />
              </div>
              <div class="form-group">
                <label class="form-label required">Postal Code</label>
                <div class="input-with-indicator">
                  <input
                    type="text" class="form-input"
                    v-model="form.postalCode"
                    @input="validatePostalCode"
                    placeholder="e.g. 100080"
                  />
                  <div class="postal-indicator" v-if="form.postalCode">
                    <div class="indicator-bar" :class="postalStatus"></div>
                    <span class="indicator-label">{{ postalLabel }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="form-row form-row-2">
              <div class="form-group">
                <label class="form-label">District</label>
                <input type="text" class="form-input" v-model="form.district" placeholder="District / county" />
              </div>
              <div class="form-group">
                <label class="form-label">Region</label>
                <input type="text" class="form-input" v-model="form.region" placeholder="State / Province" />
              </div>
            </div>
          </fieldset>

          <!-- PO Box Address -->
          <fieldset class="fieldset-block">
            <legend class="block-title">PO Box Address</legend>
            <div class="form-row form-row-2">
              <div class="form-group">
                <label class="form-label">PO Box</label>
                <input type="text" class="form-input" v-model="form.poBox" placeholder="PO Box number" />
              </div>
              <div class="form-group">
                <label class="form-label">PO Box Postal Code</label>
                <input type="text" class="form-input" v-model="form.poBoxPostal" placeholder="PO Box postal code" />
              </div>
            </div>
          </fieldset>

          <!-- Communication -->
          <fieldset class="fieldset-block">
            <legend class="block-title">Communication</legend>
            <div class="form-row form-row-4">
              <div class="form-group">
                <label class="form-label">Telephone</label>
                <input type="text" class="form-input" v-model="form.telephone" placeholder="+86 10 1234 5678" />
              </div>
              <div class="form-group">
                <label class="form-label">Mobile Phone</label>
                <input type="text" class="form-input" v-model="form.mobilePhone" placeholder="Mobile number" />
              </div>
              <div class="form-group">
                <label class="form-label">Email</label>
                <input type="email" class="form-input" v-model="form.email" placeholder="contact@company.com" />
              </div>
              <div class="form-group">
                <label class="form-label">Fax</label>
                <input type="text" class="form-input" v-model="form.fax" placeholder="Fax number" />
              </div>
            </div>
            <div class="form-row form-row-2">
              <div class="form-group">
                <label class="form-label">Website</label>
                <input type="text" class="form-input" v-model="form.website" placeholder="https://www.example.com" />
              </div>
            </div>
          </fieldset>
        </div>

        <!-- Placeholder for other tabs -->
        <div class="tab-content tab-placeholder" v-show="activeTab !== 'address'">
          <p>{{ activeTabLabel }} &mdash; content to be developed</p>
        </div>
      </div>

      <!-- Business Partner List -->
      <div class="form-card">
        <h3 class="block-title">Business Partner List</h3>
        <div v-if="error" class="error-msg">{{ error }}</div>
        <table class="bp-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Role</th>
              <th>Country</th>
              <th>City</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="loading-cell">Loading business partners...</td>
            </tr>
            <template v-else>
              <tr v-for="bp in partners" :key="bp.bp_id">
                <td class="mono">{{ bp.bp_id }}</td>
                <td>{{ bp.bp_name }}</td>
                <td>{{ bp.bp_role }}</td>
                <td>{{ bp.country }}</td>
                <td>{{ bp.city }}</td>
                <td><span class="status-tag">{{ bp.status }}</span></td>
              </tr>
              <tr v-if="partners.length === 0">
                <td colspan="6" class="empty-cell">No business partners found.</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Bottom Action Bar -->
      <div class="action-bar">
        <div class="action-left">
          <button class="btn btn-primary" @click="handleSave" :disabled="saving">
            <svg viewBox="0 0 20 20" width="16" height="16">
              <path d="M4 16V4a1 1 0 0 1 1-1h8l4 4v9a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z" fill="none" stroke="currentColor" stroke-width="1.5"/>
              <path d="M13 3v4h4M7 12h6M7 15h4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
          <button class="btn btn-secondary" @click="handleSaveContinue" :disabled="saving">
            Save &amp; Continue
          </button>
        </div>
        <button class="btn btn-border" @click="handleCancel" :disabled="saving">Cancel</button>
      </div>
    </div>
    <F4SearchModal v-model:visible="showF4" @confirm="onF4Confirm" />
    <SuccessModal v-model:visible="successVisible" :message="successMsg" @confirm="handleSuccessConfirm" />
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '@/layout/MainLayout.vue'
import F4SearchModal from '@/components/F4SearchModal.vue'
import SuccessModal from '@/components/SuccessModal.vue'
import { fetchPartners, createPartner } from '@/api'

const router = useRouter()

const successVisible = ref(false)
const successMsg = ref('')

const form = reactive({
  bpId: '',
  grouping: '',
  bpRole: '',
  salutation: '',
  lastName: '',
  firstName: '',
  searchTerm: '',
  street: '',
  houseNumber: '',
  country: '',
  city: '',
  district: '',
  postalCode: '',
  region: '',
  poBox: '',
  poBoxPostal: '',
  telephone: '',
  mobilePhone: '',
  email: '',
  fax: '',
  website: '',
})

const partners = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const error = ref('')

async function loadPartners() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchPartners()
    partners.value = res.items || []
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err.message || 'Failed to load business partners'
    console.error('Failed to fetch partners:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPartners()
})

const activeTab = ref('address')
const postalStatus = ref('')
const postalLabel = ref('')

const tabs = [
  { key: 'address', label: 'Address' },
  { key: 'address_overview', label: 'Address Overview' },
  { key: 'identification', label: 'Identification' },
  { key: 'control', label: 'Control Data' },
  { key: 'payment', label: 'Payment Transactions' },
  { key: 'status', label: 'Status' },
  { key: 'technical', label: 'Technical ID' },
]

const activeTabLabel = computed(() => {
  const t = tabs.find(t => t.key === activeTab.value)
  return t ? t.label : ''
})

function switchTab(key: string) {
  activeTab.value = key
}

function validatePostalCode() {
  const v = form.postalCode.trim()
  if (!v) { postalStatus.value = ''; postalLabel.value = ''; return }
  if (v.length < 4 || !/^\d+$/.test(v)) {
    postalStatus.value = 'error'
    postalLabel.value = 'Format Error'
  } else if (v.length === 6) {
    postalStatus.value = 'ok'
    postalLabel.value = 'Available'
  } else {
    postalStatus.value = 'warn'
    postalLabel.value = 'Format OK'
  }
}

const showF4 = ref(false)
const f4Field = ref('')

function openF4(field: string) {
  f4Field.value = field
  showF4.value = true
}
function onF4Confirm(idx: number) {
  showF4.value = false
}

function buildPayload() {
  return {
    bp_id: form.bpId || `BP${Math.floor(Math.random() * 1000000).toString().padStart(6, '0')}`,
    bp_type: form.grouping === 'INT' ? 'PERS' : 'ORG',
    bp_role: form.bpRole,
    bp_name: `${form.lastName} ${form.firstName}`.trim(),
    country: form.country,
    city: form.city,
    district: form.district || form.region || undefined,
    street: form.street,
    house_number: form.houseNumber,
    postal_code: form.postalCode,
    telephone: form.telephone,
    mobile_phone: form.mobilePhone,
    fax: form.fax,
    email: form.email,
    website: form.website,
    search_term: form.searchTerm,
    status: 'ACTIVE',
  }
}

async function handleSave() {
  if (!form.bpRole || !form.lastName || !form.firstName || !form.city || !form.country || !form.postalCode) {
    alert('Please fill in required fields: BP Role, Last Name, First Name, Country, City, Postal Code')
    return
  }
  saving.value = true
  try {
    const res = await createPartner(buildPayload())
    successMsg.value = `Business Partner ${res.bp_id} created successfully!`
    successVisible.value = true
    await loadPartners()
    Object.keys(form).forEach(key => (form as any)[key] = '')
  } catch (err: any) {
    alert('Save failed: ' + (err?.response?.data?.detail || err?.response?.data?.message || err.message))
  } finally {
    saving.value = false
  }
}

function handleSuccessConfirm() {
  successVisible.value = false
}

async function handleSaveContinue() {
  await handleSave()
}
function handleCancel() { router.push('/') }
function handleExit() { router.push('/') }
</script>

<style scoped>
.bp-page {
  padding: 32px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-title { font-size: 20px; font-weight: 700; color: #12372A; margin: 0; }
.exit-btn {
  display: inline-flex; align-items: center; gap: 6px;
  background: none; border: 1px solid rgba(173, 188, 159, 0.4); border-radius: 8px;
  padding: 8px 18px; font-size: 13px; color: rgba(18, 55, 42, 0.6);
  cursor: pointer; transition: all 0.2s; font-family: inherit;
}
.exit-btn:hover { border-color: #D9534F; color: #D9534F; background: rgba(217, 83, 79, 0.04); }

/* Form Card */
.form-card {
  background: linear-gradient(145deg, #fdfce8, #f7f5d1);
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid rgba(173, 188, 159, 0.18);
  box-shadow: 0 2px 6px rgba(173, 188, 159, 0.12);
}
.form-card-tabs { padding-top: 0; overflow: hidden; }

/* Form Row */
.form-row { display: grid; gap: 18px; margin-bottom: 16px; }
.form-row:last-child { margin-bottom: 0; }
.form-row-2 { grid-template-columns: 1fr 1fr; }
.form-row-3 { grid-template-columns: 1fr 1fr 1fr; }
.form-row-4 { grid-template-columns: 1fr 1fr 1fr 1fr; }

.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label {
  font-size: 12px; font-weight: 600; color: rgba(18, 55, 42, 0.7);
  letter-spacing: 0.3px;
}
.form-label.required::after { content: ' *'; color: #D9534F; font-weight: 700; }

.form-input, .form-select {
  height: 38px;
  border: 1px solid rgba(173, 188, 159, 0.4);
  border-radius: 8px;
  padding: 0 12px;
  font-size: 13px;
  color: #12372A;
  background: rgba(251, 250, 218, 0.4);
  font-family: inherit;
  transition: all 0.2s;
  outline: none;
  width: 100%;
}
.form-input:focus, .form-select:focus {
  border-color: #436850;
  box-shadow: 0 0 0 3px rgba(67, 104, 80, 0.08);
  background: #fff;
}
.form-input::placeholder { color: rgba(18, 55, 42, 0.25); }
.form-select { cursor: pointer; appearance: none; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 20 20' width='12' height='12' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M5 7l5 5 5-5' fill='none' stroke='%2312372A' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round' opacity='0.4'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 10px center; padding-right: 32px; }

.input-readonly {
  height: 38px; display: flex; align-items: center; padding: 0 12px;
  font-size: 13px; color: rgba(18, 55, 42, 0.35);
  background: rgba(173, 188, 159, 0.12); border-radius: 8px;
  border: 1px dashed rgba(173, 188, 159, 0.3);
}

/* Postal Code Indicator */
.input-with-indicator { position: relative; }
.postal-indicator {
  position: absolute; right: 4px; top: 50%; transform: translateY(-50%);
  display: flex; align-items: center; gap: 6px;
}
.indicator-bar {
  width: 4px; height: 20px; border-radius: 2px; transition: background 0.3s;
  background: rgba(173, 188, 159, 0.3);
}
.indicator-bar.error { background: #D9534F; }
.indicator-bar.warn { background: #F0AD4E; }
.indicator-bar.ok { background: #436850; }
.indicator-label { font-size: 10px; color: rgba(18, 55, 42, 0.4); white-space: nowrap; }

/* Tabs */
.tab-bar {
  display: flex; gap: 0;
  border-bottom: 1px solid rgba(173, 188, 159, 0.3);
  margin: 0 -24px;
  padding: 0 24px;
  background: rgba(251, 250, 218, 0.3);
  border-radius: 14px 14px 0 0;
}
.tab-btn {
  padding: 12px 18px; font-size: 12px; font-weight: 500;
  color: rgba(18, 55, 42, 0.5); background: none; border: none;
  border-bottom: 2px solid transparent; cursor: pointer;
  transition: all 0.2s; font-family: inherit; white-space: nowrap;
}
.tab-btn:hover { color: #12372A; }
.tab-btn.active {
  color: #436850; font-weight: 600; border-bottom-color: #436850;
  background: linear-gradient(to bottom, transparent, rgba(67, 104, 80, 0.04));
}
.tab-content { padding-top: 22px; }
.tab-placeholder {
  display: flex; align-items: center; justify-content: center;
  min-height: 200px; color: rgba(18, 55, 42, 0.3); font-size: 14px;
}

/* Fieldsets */
.fieldset-block {
  border: none; padding: 0; margin: 0 0 22px;
  border-bottom: 1px solid rgba(173, 188, 159, 0.15);
  padding-bottom: 18px;
}
.fieldset-block:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.block-title {
  font-size: 13px; font-weight: 700; color: #436850;
  margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
}
.block-title::before {
  content: ''; width: 4px; height: 14px; background: #436850;
  border-radius: 2px; display: inline-block;
}

/* Action Bar */
.action-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 24px;
  background: linear-gradient(145deg, #fdfce8, #f7f5d1);
  border-radius: 14px;
  border: 1px solid rgba(173, 188, 159, 0.18);
  box-shadow: 0 2px 6px rgba(173, 188, 159, 0.12);
}
.action-left { display: flex; gap: 12px; }

.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 11px 24px; font-size: 13px; font-weight: 600;
  border-radius: 8px; cursor: pointer; transition: all 0.2s;
  font-family: inherit; letter-spacing: 0.2px;
}
.btn-primary {
  background: linear-gradient(135deg, #436850, #365440); color: #FBFADA;
  border: none; box-shadow: 0 2px 8px rgba(67, 104, 80, 0.25);
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(67, 104, 80, 0.3); }
.btn-secondary {
  background: rgba(173, 188, 159, 0.2); color: #436850;
  border: 1px solid rgba(173, 188, 159, 0.35);
}
.btn-secondary:hover { background: rgba(173, 188, 159, 0.3); }
.btn-border {
  background: none; color: rgba(18, 55, 42, 0.5);
  border: 1px solid rgba(173, 188, 159, 0.35);
}
.btn-border:hover { border-color: rgba(18, 55, 42, 0.3); color: #12372A; }
.input-with-f4 { display: flex; gap: 4px; }
.input-with-f4 .form-select, .input-with-f4 .form-input { flex: 1; }
.f4-trigger {
  width: 38px; height: 38px; border: 1px solid rgba(173,188,159,0.35); border-radius: 8px;
  background: rgba(251,250,218,0.3); cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: rgba(18,55,42,0.35); transition: all 0.2s; flex-shrink: 0;
}
.f4-trigger:hover { border-color: #436850; color: #436850; background: rgba(67,104,80,0.06); }

.bp-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
.bp-table th {
  text-align: left;
  padding: 12px;
  font-size: 11px;
  color: rgba(18, 55, 42, 0.4);
  text-transform: uppercase;
  border-bottom: 1px solid rgba(173, 188, 159, 0.2);
}
.bp-table td {
  padding: 12px;
  font-size: 13px;
  color: #12372A;
  border-bottom: 1px solid rgba(173, 188, 159, 0.08);
}
.mono { font-family: monospace; }
.status-tag {
  background: rgba(67, 104, 80, 0.1);
  color: #436850;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}
.error-msg {
  color: #D9534F;
  font-size: 13px;
  padding: 10px 12px;
  background: rgba(217, 83, 79, 0.08);
  border-radius: 8px;
  margin-bottom: 12px;
}
.loading-cell, .empty-cell {
  text-align: center;
  padding: 20px;
  color: rgba(18, 55, 42, 0.4);
}
.loading-cell { font-style: italic; }
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}
</style>
