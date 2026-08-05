import { get, post, patch, del } from '../request'
import { MASTER_API } from '@/constants/api'

export interface Partner {
  bp_id: string
  bp_type: string
  bp_role: string
  bp_name: string
  country: string
  city: string
  district?: string
  street: string
  house_number?: string
  postal_code: string
  telephone: string
  mobile_phone?: string
  fax?: string
  email: string
  website?: string
  search_term: string
  status: string
}

export interface PartnerList {
  items: Partner[]
  pagination: Pagination
}

interface Pagination {
  page: number
  page_size: number
  total: number
  total_pages: number
}

export interface Material {
  material_id: string
  material_name: string
  material_type: string
  base_unit: string
  net_weight?: number
  status: string
}

export interface MaterialList {
  items: Material[]
  pagination: Pagination
}

export function fetchPartners(params?: Record<string, any>) {
  return get<PartnerList>(MASTER_API.partners, { params })
}

export function createPartner(data: Partial<Partner>) {
  return post<Partner>(MASTER_API.partners, data)
}

export function updatePartner(id: string, data: Partial<Partner>) {
  return patch<Partner>(`${MASTER_API.partners}${id}`, data)
}

export function fetchMaterials(params?: Record<string, any>) {
  return get<MaterialList>(MASTER_API.materials, { params })
}

export function createMaterial(data: Partial<Material>) {
  return post<Material>(MASTER_API.materials, data)
}

export function updateMaterial(id: string, data: Partial<Material>) {
  return patch<Material>(`${MASTER_API.materials}${id}`, data)
}

export function deleteMaterial(id: string) {
  return del<void>(`${MASTER_API.materials}${id}`)
}
