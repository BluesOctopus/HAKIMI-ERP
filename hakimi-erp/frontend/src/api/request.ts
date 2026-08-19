import axios, { AxiosError, type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import camelcaseKeys from 'camelcase-keys'
import snakecaseKeys from 'snakecase-keys'
import { clearAuth, getAuthToken } from '@/utils/auth'
import { useNotificationsStore } from '@/stores/notifications'

export interface ApiResponse<T = unknown> {
  success: boolean
  data: T
  message?: string
  detail?: string
}

const request: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

function notifyMutation(method: string | undefined, url: string | undefined, data: unknown) {
  if (!method || !url) return
  const httpMethod = method.toLowerCase()
  if (!['post', 'put', 'patch', 'delete'].includes(httpMethod)) return
  if (url.includes('/auth/') || url.includes('/assistant/')) return

  const payload = (data && typeof data === 'object' ? data : {}) as Record<string, any>
  const store = useNotificationsStore()

  const idKeys = ['salesOrderId', 'deliveryId', 'invoiceId', 'receiptId', 'quotationId', 'inquiryId', 'bpId', 'materialId', 'openArId', 'closedArId']
  let id = ''
  for (const key of idKeys) {
    if (typeof payload[key] === 'string' && payload[key]) {
      id = payload[key]
      break
    }
  }
  if (!id) {
    const match = url.match(/\/([A-Za-z0-9_-]+)(?:\/|$)/g)
    if (match) {
      const last = match[match.length - 1].replace(/\//g, '')
      if (!['deliveries', 'invoices', 'receipts', 'partners', 'materials', 'orders', 'inquiries', 'quotations', 'start-picking', 'confirm-picking', 'pick-batch', 'ship', 'pgi', 'void', 'from-delivery', 'pricing-conditions', 'sales-organizations'].includes(last)) {
        id = last
      }
    }
  }

  const titleFor = (created: string, updated: string, deleted?: string): string => {
    if (httpMethod === 'delete' && deleted) return deleted
    return httpMethod === 'post' ? created : updated
  }
  const idText = (prefix: string, suffix: string): string => (id ? `${prefix} ${id} ${suffix}` : `${prefix}${suffix}`)

  let title = ''
  let text = ''
  let tone: 'success' | 'warning' | 'danger' = 'success'

  if (url.includes('/sales/inquiries')) {
    title = titleFor('Inquiry created', 'Inquiry updated')
    text = idText('Inquiry', 'has been processed.')
  } else if (url.includes('/sales/quotations')) {
    title = titleFor('Quotation created', 'Quotation updated')
    text = idText('Quotation', 'has been processed.')
  } else if (url.includes('/sales/orders')) {
    if (httpMethod === 'delete') {
      tone = 'danger'
      title = 'Sales order deleted'
      text = id ? `Sales order ${id} has been deleted.` : 'Sales order has been deleted.'
    } else {
      title = titleFor('Sales order created', 'Sales order updated')
      text = id ? `Sales order ${id} has been processed.` : 'Sales order has been processed.'
    }
  } else if (url.includes('/logistics/deliveries')) {
    if (url.includes('/from-so/')) {
      title = 'Delivery created'
      text = id ? `Delivery ${id} was created from the sales order.` : 'Delivery created.'
    } else if (url.includes('/start-picking')) {
      title = 'Picking started'
      text = id ? `Delivery ${id} has started picking.` : 'Picking started.'
    } else if (url.includes('/confirm-picking')) {
      title = 'Picking confirmed'
      text = id ? `Delivery ${id} picking confirmed.` : 'Picking confirmed.'
    } else if (url.includes('/pick-batch')) {
      title = 'Batch picking completed'
      text = id ? `Batch picking completed for delivery ${id}.` : 'Batch picking completed.'
    } else if (url.includes('/ship')) {
      title = 'Delivery shipped'
      text = id ? `Delivery ${id} has shipped.` : 'Delivery shipped.'
    } else if (url.includes('/pgi')) {
      title = 'Goods issue posted'
      text = id ? `Goods issue posted for delivery ${id}.` : 'Goods issue posted.'
    } else {
      title = 'Delivery updated'
      text = id ? `Delivery ${id} has been processed.` : 'Delivery processed.'
    }
  } else if (url.includes('/finance/invoices/from-delivery/')) {
    title = 'Invoice created'
    text = id ? `Invoice ${id} has been created.` : 'Invoice created.'
  } else if (url.includes('/finance/invoices') && url.includes('/void')) {
    tone = 'warning'
    title = 'Invoice voided'
    text = id ? `Invoice ${id} has been voided.` : 'Invoice voided.'
  } else if (url.includes('/finance/invoices')) {
    title = 'Invoice updated'
    text = id ? `Invoice ${id} has been processed.` : 'Invoice processed.'
  } else if (url.includes('/finance/receipts')) {
    title = 'Receipt created'
    text = id ? `Receipt ${id} has been recorded.` : 'Receipt recorded.'
  } else if (url.includes('/master/partners')) {
    if (httpMethod === 'delete') {
      tone = 'danger'
      title = 'Business partner deleted'
      text = id ? `Business partner ${id} has been deleted.` : 'Business partner deleted.'
    } else {
      title = 'Business partner saved'
      text = id ? `Business partner ${id} has been processed.` : 'Business partner processed.'
    }
  } else if (url.includes('/master/materials/pricing-conditions')) {
    title = 'Pricing conditions updated'
    text = 'Material pricing conditions saved.'
  } else if (url.includes('/master/materials/sales-organizations')) {
    title = 'Sales organizations updated'
    text = 'Sales organization data saved.'
  } else if (url.includes('/master/materials')) {
    if (httpMethod === 'delete') {
      tone = 'danger'
      title = 'Material deleted'
      text = id ? `Material ${id} has been deleted.` : 'Material deleted.'
    } else {
      title = 'Material saved'
      text = id ? `Material ${id} has been processed.` : 'Material processed.'
    }
  } else if (httpMethod === 'delete') {
    tone = 'danger'
    title = 'Record deleted'
    text = id ? `Record ${id} has been deleted.` : 'Record deleted.'
  } else {
    title = httpMethod === 'post' ? 'Operation completed' : 'Record updated'
    text = id ? `Record ${id} has been processed.` : 'The system processed your request.'
  }

  store.push({ title, text, tone })
}

request.interceptors.request.use(
  (config) => {
    const token = getAuthToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 自动转换发送的数据为 snake_case
    if (config.data && !(config.data instanceof FormData)) {
      config.data = snakecaseKeys(config.data, { deep: true })
    }
    // 自动转换 URL 参数为 snake_case
    if (config.params) {
      config.params = snakecaseKeys(config.params, { deep: true })
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // 自动转换接收的数据为 camelCase
    if (response.data && response.data.data) {
      response.data.data = camelcaseKeys(response.data.data, { deep: true })
    }
    notifyMutation(response.config.method, response.config.url, response.data.data)
    return response
  },
  (error: AxiosError<ApiResponse>) => {
    const url = error.config?.url || ''
    const isAuthEndpoint = url.includes('/auth/login') || url.includes('/auth/register') || url.includes('/auth/logout')

    if (error.response?.status === 401 && !isAuthEndpoint) {
      clearAuth()
      const redirect = encodeURIComponent(window.location.pathname + window.location.search)
      if (window.location.pathname !== '/login') {
        window.location.assign(`/login?redirect=${redirect}`)
      }
    }

    let message = ''
    const data = error.response?.data
    
    if (data) {
      if (data.message) {
        message = data.message
      } else if (data.detail) {
        if (Array.isArray(data.detail)) {
          // 处理 FastAPI 422 验证错误
          message = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join('; ')
        } else {
          message = data.detail
        }
      }
    }

    if (!message) {
      message = error.message || 'Network error'
    }
    
    return Promise.reject(new Error(message))
  }
)

export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const res = await request.get<ApiResponse<T>>(url, config)
  return res.data.data
}

export async function post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const res = await request.post<ApiResponse<T>>(url, data, config)
  return res.data.data
}

export async function put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const res = await request.put<ApiResponse<T>>(url, data, config)
  return res.data.data
}

export async function del<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const res = await request.delete<ApiResponse<T>>(url, config)
  return res.data.data
}

export default request
