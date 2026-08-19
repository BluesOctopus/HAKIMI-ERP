import { watch } from 'vue'
import { usePreferencesStore } from '@/stores/preferences'

const EXTRA_UI_TEXT: Record<string, string> = {
  "Home": "首页",
  "Dashboard": "仪表盘",
  "Account": "账户",
  "Account menu": "账户菜单",
  "Action": "操作",
  "Customer": "客户",
  "Customer Name": "客户名称",
  "Address": "地址",
  "City": "城市",
  "Country": "国家",
  "Country / Region": "国家/地区",
  "Contact": "联系人",
  "Description": "描述",
  "Date": "日期",
  "Time": "时间",
  "Status": "状态",
  "Type": "类型",
  "Name": "名称",
  "Amount": "金额",
  "Quantity": "数量",
  "Unit Price": "单价",
  "Net Price": "净价",
  "Net Value": "净值",
  "Currency": "币种",
  "Role": "角色",
  "Email": "邮箱",
  "Username": "用户名",
  "Password": "密码",
  "Confirm password": "确认密码",
  "First Name": "名",
  "Last Name": "姓",
  "Full name": "全名",
  "Sign in": "登录",
  "Sign in to continue": "登录以继续",
  "Sign out": "退出登录",
  "Create Account": "创建账户",
  "Register a new HAKIMI ERP user": "注册新的 HAKIMI ERP 用户",
  "Already have an account?": "已有账户？",
  "Don't have an account?": "没有账户？",
  "Remember login state": "记住登录状态",
  "Username or email": "用户名或邮箱",
  "At least 3 characters": "至少 3 个字符",
  "At least 6 characters": "至少 6 个字符",
  "Enter password": "输入密码",
  "Enter first name": "输入名",
  "Enter last name": "输入姓",
  "Enter city": "输入城市",
  "Repeat password": "重复密码",
  "Search": "查询",
  "Search Term": "搜索词",
  "Search keyword": "搜索关键词",
  "Quick search keyword": "快速搜索关键词",
  "Search by ID, name, or bin...": "按 ID、名称或仓位搜索...",
  "Reset": "重置",
  "Save": "保存",
  "Save & Continue": "保存并继续",
  "Cancel": "取消",
  "Confirm": "确认",
  "Delete": "删除",
  "Edit": "编辑",
  "View": "查看",
  "View Details": "查看详情",
  "Export": "导出",
  "Print": "打印",
  "Retry": "重试",
  "Exit": "退出",
  "Back": "返回",
  "Back to Monitor": "返回监控",
  "Close": "关闭",
  "OK": "确定",
  "Send": "发送",
  "Loading...": "加载中...",
  "Syncing...": "同步中...",
  "Syncing data...": "数据同步中...",
  "Initializing...": "初始化中...",
  "Auto Refresh": "自动刷新",
  "All Statuses": "全部状态",
  "Creating": "创建中",
  "Picking": "拣配中",
  "Picked": "已拣配",
  "In Transit": "运输中",
  "Completed": "已完成",
  "Cancelled": "已取消",
  "Open": "打开",
  "Pending": "待处理",
  "Cleared": "已清账",
  "Closed": "已关闭",
  "Void": "已作废",
  "Partial": "部分",
  "Unpaid": "未付",
  "Outstanding": "未清",
  "Overdue": "逾期",
  "Already Issued": "已开票",
  "Already Picked": "已拣配",
  "Continue Picking": "继续拣配",
  "Record Pick Batch": "记录拣配批次",
  "Pick Batch": "拣配批次",
  "Confirm Picking Complete": "确认拣配完成",
  "Post Goods Issue": "发货过账",
  "Start Picking": "开始拣配",
  "Ship": "发货",
  "Collect Payment": "收款",
  "Payment Collected": "已收款",
  "Payment Posted": "付款已过账",
  "Payment Method": "付款方式",
  "Payment Terms": "付款条件",
  "Payment History": "付款历史",
  "Payment Amount": "付款金额",
  "Bank Transfer": "银行转账",
  "Cash": "现金",
  "Credit Card": "信用卡",
  "Business Partner": "业务伙伴",
  "Business Partner List": "业务伙伴列表",
  "Business Partner Master": "业务伙伴主数据",
  "Business Partner No.": "业务伙伴编号",
  "BP ID": "业务伙伴 ID",
  "Material": "物料",
  "Material Master": "物料主数据",
  "Material List": "物料列表",
  "Material No.": "物料编号",
  "Material Group": "物料组",
  "Material Type": "物料类型",
  "Material Desc.": "物料描述",
  "Product": "产品",
  "Product Catalog": "产品目录",
  "Product ID": "产品 ID",
  "Sales Organization": "销售组织",
  "Sales Org": "销售组织",
  "Sales Office": "销售办公室",
  "Sales Group": "销售组",
  "Dist. Channel": "分销渠道",
  "Division": "产品组",
  "Plant": "工厂",
  "Storage Location": "存储地点",
  "Storage Loc": "存储地点",
  "Warehouse": "仓库",
  "Shipping Point": "发货点",
  "Carrier / Driver": "承运人/司机",
  "Delivering Plant": "交货工厂",
  "Delivery Block": "发货冻结",
  "Billing Block": "开票冻结",
  "Delivery Date": "发货日期",
  "GI Date": "过账日期",
  "Planned GI Date": "计划发货过账日期",
  "Due Date": "到期日",
  "Valid From": "有效期自",
  "Valid To": "有效期至",
  "Valid Until": "有效期至",
  "Sales Order": "销售订单",
  "Sales Order No.": "销售订单号",
  "Order Type": "订单类型",
  "Order Qty": "订单数量",
  "Delivery Qty": "发货数量",
  "Del Qty": "发货数量",
  "Del. No.": "发货单号",
  "Delivery No.": "发货单号",
  "Delivery List": "发货单列表",
  "Inquiry": "询价",
  "Inquiry Management": "询价管理",
  "Inquiry No.": "询价单号",
  "Inquiry Type": "询价类型",
  "Inquiry Date": "询价日期",
  "Quotation Management": "报价管理",
  "Quotation No.": "报价单号",
  "Quotation Type": "报价类型",
  "Quotation (QT)": "报价 (QT)",
  "Invoice": "发票",
  "Invoice Management": "发票管理",
  "Invoice No.": "发票号",
  "Invoice Date": "发票日期",
  "Invoice Amount": "发票金额",
  "Invoice Detail": "发票详情",
  "Receivable Detail": "应收详情",
  "Account Receivables": "应收账款",
  "Accounts Receivable Report": "应收账款报表",
  "Unpaid Accounts Receivable": "未收应收账款",
  "Received Amount": "已收金额",
  "Unpaid Amount": "未收金额",
  "Total Unpaid": "未收合计",
  "Total Receipts": "收款合计",
  "Total Invoiced": "开票合计",
  "Total Outstanding": "未清合计",
  "Total Overdue": "逾期合计",
  "Outstanding AR": "未清应收",
  "Collection Progress": "收款进度",
  "Collection Rate": "收款率",
  "Collection Ratio": "收款比例",
  "Collection ratio": "收款比例",
  "Recovery ratio": "回款比例",
  "Avg Days to Collect": "平均收款天数",
  "Days Overdue": "逾期天数",
  "Month Collected": "当月已收",
  "This Period Collected": "本期已收",
  "This Period Invoiced": "本期开票",
  "All-time receipts": "全部收款",
  "Beginning Balance": "期初余额",
  "Ending Balance": "期末余额",
  "Past due date": "已逾期",
  "AR Aging Analysis": "应收账龄分析",
  "Top 5 Outstanding Customers": "前 5 名未清客户",
  "Collection Trend (6 Months)": "收款趋势（6 个月）",
  "Basic Information": "基本信息",
  "General Data": "一般数据",
  "Tax Numbers": "税号",
  "ID Numbers": "证件号码",
  "ID Type": "证件类型",
  "ID Number": "证件号码",
  "Tax": "税",
  "Tax ID 1 (VAT)": "税号 1（VAT）",
  "Tax ID 2": "税号 2",
  "Reference": "参考",
  "Reference No.": "参考号",
  "Ref Inquiry": "参考询价",
  "Item": "行项目",
  "Item Category": "行项目类别",
  "Item Description": "行项目描述",
  "Expected Value": "期望金额",
  "Incoterms": "贸易条款",
  "Ship-to": "收货方",
  "Ship. Condition": "装运条件",
  "Deliv. Priority": "发货优先级",
  "Req. Deliv. Date": "要求交货日期",
  "Restrictions": "限制",
  "Dimensions": "尺寸",
  "Weight Unit": "重量单位",
  "Volume": "体积",
  "Gross Weight": "毛重",
  "Net Weight": "净重",
  "Base UoM": "基本单位",
  "UoM": "单位",
  "Bin": "仓位",
  "Stock": "库存",
  "Standard Address": "标准地址",
  "Main Address": "主要地址",
  "Street": "街道",
  "House No.": "门牌号",
  "Postal Code": "邮政编码",
  "Select": "请选择",
  "Select country": "选择国家",
  "Select role": "选择角色",
  "Select ID Type": "选择证件类型",
  "Select grouping": "选择分组",
  "-- Select Customer --": "-- 选择客户 --",
  "-- Select Material --": "-- 选择物料 --",
  "Grouping": "分组",
  "Group": "组",
  "Salutation": "称谓",
  "Mr.": "先生",
  "Mrs.": "女士",
  "Ms.": "女士",
  "Dr.": "博士",
  "Passport": "护照",
  "External": "外部",
  "Internal": "内部",
  "Method": "方式",
  "Check": "检查",
  "Check Availability": "检查可用性",
  "Simulate ATP": "模拟 ATP",
  "F4 Search": "F4 搜索",
  "Pages": "页面",
  "Go to": "前往",
  "10 / page": "10 / 页",
  "Auto-generated if empty": "为空时自动生成",
  "Input ID or leave for random": "输入 ID，留空则自动生成",
  "Optional": "可选",
  "Legacy system ID": "旧系统 ID",
  "Operator name": "操作员姓名",
  "Enter Tax ID": "输入税号",
  "Enter registration number": "输入注册号",
  "Enter tax identification number": "输入税号",
  "Street name": "街道名称",
  "House number": "门牌号",
  "Customer (BP)": "客户（BP）",
  "Customer (FLCU01)": "客户（FLCU01）",
  "Vendor (FLVN00)": "供应商（FLVN00）",
  "Help": "帮助",
  "Notifications": "通知",
  "Mark as read": "标记为已读",
  "Clear conversation": "清空对话",
  "Ask a question...": "问一个问题...",
  "Ask the assistant (drag to move)": "向助手提问（可拖动）",
  "Navigation & workflow guide": "导航与工作流指南",
  "HAKIMI Assistant": "HAKIMI 助手",
  "HAKIMI ERP · Finance Department": "HAKIMI ERP · 财务部",
  "Billing documents and status tracking.": "开票单据与状态跟踪。",
  "Browse and manage product listings with pricing and availability.": "浏览并管理产品列表、价格与可用性。",
  "Create and manage customers and vendors across the organization.": "创建并管理企业内的客户与供应商。",
  "Create and manage material master records across all organizational levels.": "创建并管理各组织层级的物料主数据。",
  "Define and maintain pricing condition records for materials and customers.": "定义并维护物料与客户的定价条件记录。",
  "Configure sales org structure, distribution channels, and divisions.": "配置销售组织结构、分销渠道与产品组。",
  "Manage customer quotes and convert them to sales orders.": "管理客户报价并将其转为销售订单。",
  "Track and manage customer inquiries, convert to quotations.": "跟踪并管理客户询价，并转为报价。",
  "View and manage all delivery orders.": "查看并管理所有发货单。",
  "Monitor all accounts and collection progress.": "监控所有账户与收款进度。",
  "Monitor collection progress in real time.": "实时监控收款进度。",
  "Current stage reflects the invoice and receivable status.": "当前阶段反映发票与应收状态。",
  "Invoice Summary by Status": "按状态汇总发票",
  "Receipt Ledger": "收款台账",
  "Overdue Receivables Analysis": "逾期应收分析",
  "Invoice Status Distribution": "发票状态分布",
  "Efficiency Index": "效率指数",
  "All fields": "所有字段",
  "Across all clients": "所有客户",
  "Create one": "创建一个",
  "Continue": "继续",
  "Report generation completed. Detailed visualization for this report type is coming soon.": "报表生成完成，该报表类型的详细可视化即将推出。",
  "All items fully picked. You may now Confirm Picking Complete.": "所有行项目均已拣齐，现在可以确认拣配完成。",
  "Enter integer goods issue quantities. Cannot exceed picked quantity.": "请输入整数发货过账数量，不能超过已拣数量。",
  "No address information entered yet.": "尚未录入地址信息。",
  "No business partners found.": "未找到业务伙伴。",
  "No materials found.": "未找到物料。",
  "No products found.": "未找到产品。",
  "No pricing conditions found.": "未找到定价条件。",
  "No sales organizations found.": "未找到销售组织。",
  "No deliveries found.": "未找到发货单。",
  "No quotations found.": "未找到报价。",
  "No inquiries found.": "未找到询价。",
  "No invoices found.": "未找到发票。",
  "No entries found.": "未找到记录。",
  "No payment records.": "暂无付款记录。",
  "No receipt records found": "未找到收款记录",
  "No receivable records found.": "未找到应收记录。",
  "No unpaid receivables found.": "未找到未收应收。",
  "No outstanding receivables": "无未清应收",
  "No overdue receivables": "无逾期应收",
  "No collection records in the past 6 months": "过去 6 个月无收款记录",
  "Loading business partners...": "正在加载业务伙伴...",
  "Loading materials...": "正在加载物料...",
  "Loading products...": "正在加载产品...",
  "Loading pricing conditions...": "正在加载定价条件...",
  "Loading sales organizations...": "正在加载销售组织...",
  "Loading deliveries...": "正在加载发货单...",
  "Loading delivery details...": "正在加载发货单详情...",
  "Loading receivable details...": "正在加载应收详情...",
  "This Batch": "本批次",
  "Picked / Total": "已拣 / 总计",
  "Delivery Progress": "发货进度",
  "Order Items & Picking Status": "订单行项目与拣配状态",
  "Shipment Information": "发运信息",
  "Customer & Terms": "客户与条款",
  "Payment": "付款",
  "Receipt No.": "收款单号",
  "Invoice Items": "发票行项目",
  "Collection": "收款",
  "Total": "合计",
  "Percentage": "百分比",
  "Count": "数量",
  "Uncollected": "未收款",
  "Overdue Amount": "逾期金额"
}

const textState = new WeakMap<Text, { original: string; translated?: string }>()
const attrState = new WeakMap<Element, Map<string, { original: string; translated?: string }>>()

function normalize(value: string): string {
  return value.replace(/\s+/g, ' ').trim()
}

function translateText(value: string, locale: string): string {
  if (locale !== 'zh') return value
  const key = normalize(value)
  if (!key) return value
  return EXTRA_UI_TEXT[key] ?? value
}

function shouldSkipNode(node: Text): boolean {
  const parent = node.parentElement
  if (!parent) return true
  if (parent.closest('script,style,code,pre,textarea')) return true
  if (parent.closest('[data-no-translate]')) return true
  if (parent.closest('td')) {
    if (!parent.closest('button,a,.link,.empty-cell')) return true
  }
  if (parent.closest('.mono,.stag') && !parent.closest('button,a,.link,.empty-cell')) return true
  return false
}

function translateNode(node: Text, locale: string): void {
  if (shouldSkipNode(node)) return
  const raw = node.nodeValue ?? ''
  const trimmed = raw.trim()
  if (!trimmed) return

  if (locale !== 'zh') {
    const state = textState.get(node)
    if (!state) return
    if (raw === state.translated) {
      node.nodeValue = state.original
    }
    textState.delete(node)
    return
  }

  let state = textState.get(node)
  if (!state || (raw !== state.original && raw !== state.translated)) {
    state = { original: raw }
    textState.set(node, state)
  }

  const source = state.original
  const sourceTrimmed = source.trim()
  const replacement = translateText(sourceTrimmed, locale)
  if (replacement === sourceTrimmed) return
  const start = source.indexOf(sourceTrimmed)
  const end = start + sourceTrimmed.length
  const next = source.slice(0, start) + replacement + source.slice(end)
  if (next !== raw) node.nodeValue = next
  state.translated = next
}

const ATTRIBUTES = ['placeholder', 'title', 'aria-label'] as const

function translateAttributes(root: ParentNode, locale: string): void {
  const selector = ATTRIBUTES.map((attr) => `[${attr}]`).join(',')
  root.querySelectorAll?.(selector).forEach((element) => {
    ATTRIBUTES.forEach((attr) => {
      const current = element.getAttribute(attr)
      if (!current || !/[A-Za-z]/.test(current)) return
      let map = attrState.get(element)
      if (!map) {
        map = new Map()
        attrState.set(element, map)
      }
      let state = map.get(attr)
      if (locale !== 'zh') {
        if (state && current === state.translated) {
          element.setAttribute(attr, state.original)
        }
        map.delete(attr)
        return
      }
      if (!state || (current !== state.original && current !== state.translated)) {
        state = { original: current }
        map.set(attr, state)
      }
      const translated = translateText(current, locale)
      if (translated !== current) {
        element.setAttribute(attr, translated)
        state.translated = translated
      }
    })
  })
}

function applyTranslations(root: ParentNode, locale: string): void {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT)
  const nodes: Text[] = []
  while (walker.nextNode()) {
    const node = walker.currentNode as Text
    if (node.parentElement && !shouldSkipNode(node)) nodes.push(node)
  }
  nodes.forEach((node) => translateNode(node, locale))
  translateAttributes(root, locale)
}

let observer: MutationObserver | null = null
let scheduled = false

export function startDomTranslator(): void {
  const preferences = usePreferencesStore()
  const run = () => {
    scheduled = false
    applyTranslations(document.body, preferences.locale)
  }
  const schedule = () => {
    if (scheduled) return
    scheduled = true
    queueMicrotask(run)
  }

  observer = new MutationObserver(schedule)
  observer.observe(document.body, { childList: true, subtree: true, characterData: true })

  watch(() => preferences.locale, () => schedule(), { flush: 'post' })
  schedule()
}

export function stopDomTranslator(): void {
  observer?.disconnect()
  observer = null
}
