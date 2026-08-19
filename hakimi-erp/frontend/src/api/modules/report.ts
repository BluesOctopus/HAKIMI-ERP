import { get } from '../request'

const BASE = '/api/v1/reports'

export function fetchSalesPerformance(params?: { days?: number }) {
  return get<any>(`${BASE}/sales-performance`, { params })
}

export function fetchFinancialSummary() {
  return get<any>(`${BASE}/financial-summary`)
}

export function fetchFinancialDetail() {
  return get<any>(`${BASE}/financial-detail`)
}

export function fetchDeliveryStats() {
  return get<any>(`${BASE}/delivery-stats`)
}

export function fetchCustomerAnalysis() {
  return get<any>(`${BASE}/customer-analysis`)
}

export function fetchInventoryTurnover() {
  return get<any>(`${BASE}/inventory-turnover`)
}

export function fetchPricingConditionsReport() {
  return get<any>(`${BASE}/pricing-conditions`)
}

export function fetchTaxComplianceReport() {
  return get<any>(`${BASE}/tax-compliance`)
}

export function fetchQuotationConversionReport() {
  return get<any>(`${BASE}/quotation-conversion`)
}

export function fetchDashboardSummary() {
  return get<any>(`${BASE}/dashboard-summary`)
}

