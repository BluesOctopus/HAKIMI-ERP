import { get, post, put } from '../request'
import { LOGISTICS_API } from '@/constants/api'

export interface DeliveryItem {
  delivery_item_id: string
  item_no: number
  sales_order_id?: string
  so_item_id?: string
  material_id: string
  delivery_quantity: number
  picked_quantity?: number
  plant?: string
  storage_location?: string
  status: string
}

export interface Delivery {
  delivery_id: string
  sales_order_id?: string
  customer_id: string
  shipping_point?: string
  planned_gi_date?: string
  actual_gi_date?: string
  status: string
  items: DeliveryItem[]
  created_time?: string
}

export interface DeliveryList {
  items: Delivery[]
  pagination: Pagination
}

interface Pagination {
  page: number
  page_size: number
  total: number
  total_pages: number
}

export function fetchDeliveries(params?: Record<string, any>) {
  return get<DeliveryList>(LOGISTICS_API.deliveries, { params })
}

export function fetchDeliveryById(id: string) {
  return get<Delivery>(LOGISTICS_API.deliveryById(id))
}

export function createDeliveryFromSalesOrder(soId: string) {
  return post<Delivery>(LOGISTICS_API.createFromSo(soId))
}

export function postGoodsIssue(deliveryId: string) {
  return post<Delivery>(LOGISTICS_API.postPgi(deliveryId))
}

export function updateDelivery(id: string, data: Partial<Delivery>) {
  return put<Delivery>(LOGISTICS_API.deliveryById(id), data)
}
