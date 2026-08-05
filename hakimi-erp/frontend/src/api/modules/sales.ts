import { get, post, put, del } from '../request'
import { SALES_API } from '@/constants/api'

export interface InquiryItem {
  inquiry_item_id: string
  item_no: number
  material_id: string
  item_description?: string
  order_quantity: number
  expected_order_value?: number
  sales_unit: string
}

export interface Inquiry {
  inquiry_id: string
  inquiry_type: string
  customer_id: string
  customer_reference?: string
  valid_from?: string
  valid_to?: string
  requested_delivery_date?: string
  sales_org: string
  distribution_channel: string
  division: string
  status: string
  items: InquiryItem[]
  created_time?: string
}

export interface InquiryList {
  items: Inquiry[]
  pagination: Pagination
}

interface Pagination {
  page: number
  page_size: number
  total: number
  total_pages: number
}

export interface QuotationItem {
  quotation_item_id: string
  item_no: number
  material_id: string
  order_quantity: number
  sales_unit: string
  unit_price?: number
  net_price?: number
}

export interface Quotation {
  quotation_id: string
  quotation_type: string
  inquiry_id?: string
  customer_id: string
  valid_from?: string
  valid_to?: string
  payment_terms?: string
  incoterms?: string
  status: string
  net_value?: number
  items: QuotationItem[]
}

export interface QuotationList {
  items: Quotation[]
  pagination: Pagination
}

export interface SalesOrderItem {
  so_item_id: string
  item_no: number
  material_id: string
  item_category?: string
  order_quantity: number
  plant?: string
  sales_unit: string
}

export interface SalesOrder {
  sales_order_id: string
  order_type: string
  quotation_id?: string
  customer_id: string
  customer_reference?: string
  requested_delivery_date?: string
  pricing_date?: string
  shipping_condition?: string
  delivery_priority?: string
  status: string
  net_value?: number
  items: SalesOrderItem[]
  created_time?: string
}

export interface SalesOrderList {
  items: SalesOrder[]
  pagination: Pagination
}

// Inquiry APIs
export function fetchInquiries(params?: Record<string, any>) {
  return get<InquiryList>(SALES_API.inquiries, { params })
}

export function fetchInquiryById(id: string) {
  return get<Inquiry>(SALES_API.inquiryById(id))
}

export function createInquiry(data: Partial<Inquiry>) {
  return post<Inquiry>(SALES_API.inquiries, data)
}

export function updateInquiry(id: string, data: Partial<Inquiry>) {
  return put<Inquiry>(SALES_API.inquiryById(id), data)
}

// Quotation APIs
export function fetchQuotations(params?: Record<string, any>) {
  return get<QuotationList>(SALES_API.quotations, { params })
}

export function fetchQuotationById(id: string) {
  return get<Quotation>(SALES_API.quotationById(id))
}

export function createQuotation(data: Partial<Quotation>) {
  return post<Quotation>(SALES_API.quotations, data)
}

export function updateQuotation(id: string, data: Partial<Quotation>) {
  return put<Quotation>(SALES_API.quotationById(id), data)
}

// Sales Order APIs
export function fetchOrders(params?: Record<string, any>) {
  return get<SalesOrderList>(SALES_API.orders, { params })
}

export function fetchOrderById(id: string) {
  return get<SalesOrder>(SALES_API.orderById(id))
}

export function createOrder(data: Partial<SalesOrder>) {
  return post<SalesOrder>(SALES_API.orders, data)
}

export function updateOrder(id: string, data: Partial<SalesOrder>) {
  return put<SalesOrder>(SALES_API.orderById(id), data)
}

export function deleteOrder(id: string) {
  return del<void>(SALES_API.orderById(id))
}
