import { get, post, put } from '../request'
import { FINANCE_API } from '@/constants/api'

export interface InvoiceItem {
  invoice_item_id: string
  item_no: number
  material_id: string
  quantity?: number
  unit_price?: number
  tax_amount?: number
  net_price?: number
}

export interface Invoice {
  invoice_id: string
  delivery_id?: string
  sales_order_id?: string
  billing_type: string
  invoice_date: string
  billing_date: string
  sold_to_party?: string
  payer?: string
  currency: string
  total_amount?: number
  status: string
  items: InvoiceItem[]
  created_time?: string
}

export interface InvoiceList {
  items: Invoice[]
  pagination: Pagination
}

interface Pagination {
  page: number
  page_size: number
  total: number
  total_pages: number
}

export interface OpenAccountReceivable {
  open_ar_id: string
  invoice_id: string
  receivable_amount: number
  received_amount: number
  due_date?: string
  status: string
  created_time?: string
}

export interface ClosedAccountReceivable {
  closed_ar_id: string
  invoice_id: string
  receivable_amount: number
  received_amount: number
  created_time?: string
  closed_time?: string
}

export interface ReceivableList {
  items: (OpenAccountReceivable | ClosedAccountReceivable)[]
  pagination: Pagination
}

export interface Receipt {
  receipt_id: string
  invoice_id: string
  payer: string
  receipt_amount: number
  payment_method?: string
  currency: string
  reference_no?: string
  receipt_date?: string
}

export function fetchInvoices(params?: Record<string, any>) {
  return get<InvoiceList>(FINANCE_API.invoices, { params })
}

export function fetchInvoiceById(id: string) {
  return get<Invoice>(FINANCE_API.invoiceById(id))
}

export function createInvoiceFromDelivery(deliveryId: string) {
  return post<Invoice>(FINANCE_API.invoiceFromDelivery(deliveryId))
}

export function fetchOpenAR(params?: Record<string, any>) {
  return get<ReceivableList>(FINANCE_API.arOpen, { params })
}

export function fetchClosedAR(params?: Record<string, any>) {
  return get<ReceivableList>(FINANCE_API.arClosed, { params })
}

export function createReceipt(data: Partial<Receipt>) {
  return post<Receipt>(FINANCE_API.receipts, data)
}

export function updateInvoice(id: string, data: Partial<Invoice>) {
  return put<Invoice>(FINANCE_API.invoiceById(id), data)
}
