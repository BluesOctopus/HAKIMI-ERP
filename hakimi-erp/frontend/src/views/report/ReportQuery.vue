<template>
  <div class="page">
    <div class="header-card">
      <div class="hc-left">
        <div class="hc-icon"><svg viewBox="0 0 24 24" width="22" height="22"><rect x="3" y="3" width="7" height="7" rx="1" fill="none" stroke="#436850" stroke-width="1.8"/><rect x="14" y="3" width="7" height="7" rx="1" fill="none" stroke="#436850" stroke-width="1.8"/><rect x="3" y="14" width="7" height="7" rx="1" fill="none" stroke="#436850" stroke-width="1.8"/><rect x="14" y="14" width="7" height="7" rx="1" fill="none" stroke="#436850" stroke-width="1.8"/></svg></div>
        <div class="hc-text"><h2 class="hc-title">{{ t('report.title') }}</h2><p class="hc-sub">{{ t('report.subtitle') }}</p></div>
      </div>
    </div>

    <div class="report-grid" v-if="!activeReport">
      <div class="report-card" v-for="r in reports" :key="r.id">
        <div class="rc-icon" v-html="r.icon"></div>
        <div class="rc-body">
          <h3 class="rc-title">{{ reportTitle(r.id) }}</h3>
          <p class="rc-desc">{{ reportDesc(r.id) }}</p>
          <div class="rc-meta">
            <span class="rc-tag">{{ r.category }}</span>
            <span class="rc-date">{{ t('report.updated') }}: {{ r.updated }}</span>
          </div>
          <button class="btn btn-primary rc-btn" @click="runReport(r)">{{ t('report.run') }}</button>
        </div>
      </div>
    </div>

    <!-- Result View -->
    <div v-else class="result-container">
      <div class="result-header">
        <button class="back-link" @click="activeReport = null">
          <svg viewBox="0 0 20 20" width="16" height="16"><path d="M12 4l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {{ t('report.back') }}
        </button>
        <div class="rh-main">
          <h3>{{ reportTitle(activeReport.id) }}</h3>
          <div class="rh-actions">
            <select v-if="activeReport.id === 1" class="period-select" v-model.number="salesDays" @change="refreshReport">
              <option :value="7">{{ t('report.last7') }}</option>
              <option :value="30">{{ t('report.last30') }}</option>
              <option :value="90">{{ t('report.last90') }}</option>
              <option :value="365">{{ t('report.last365') }}</option>
            </select>
            <button class="btn btn-outline btn-sm" @click="exportData">{{ t('report.export') }}</button>
            <button class="btn btn-primary btn-sm" @click="refreshReport">{{ t('report.refresh') }}</button>
          </div>
        </div>
      </div>

      <!-- Mode selector for Financial Summary -->
      <div v-if="activeReport.id === 3" class="mode-selector">
        <button
          class="mode-btn"
          :class="{ active: finMode === 'overview' }"
          @click="finMode = 'overview'"
        >
          <svg viewBox="0 0 20 20" width="16" height="16"><path d="M3 20h2V10H3v10zm6 0h2V4H9v16zm6 0h2v-7h-2v7zm6 0h2V7h-2v13z" fill="currentColor"/></svg>
          {{ t('report.overview') }}
        </button>
        <button
          class="mode-btn"
          :class="{ active: finMode === 'statement' }"
          @click="finMode = 'statement'"
        >
          <svg viewBox="0 0 20 20" width="16" height="16"><rect x="2" y="3" width="16" height="14" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5 7h10M5 10h10M5 13h7" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>
          {{ t('report.statement') }}
        </button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>{{ t('report.loading') }}</p>
      </div>

      <div v-else-if="reportData" class="report-content">
        <!-- Sales Performance View -->
        <div v-if="activeReport.id === 1" class="data-view">
          <div class="kpi-row">
            <div class="kpi-card">
              <label>{{ t('sales.totalOrders') }}</label>
              <div class="value">{{ salesSummary.totalOrders }}</div>
            </div>
            <div class="kpi-card">
              <label>{{ t('sales.totalRevenue') }}</label>
              <div class="value">¥{{ fmt(salesSummary.totalRevenue) }}</div>
            </div>
            <div class="kpi-card">
              <label>{{ t('sales.avgOrder') }}</label>
              <div class="value">¥{{ fmt(salesSummary.avgValue) }}</div>
            </div>
            <div class="kpi-card success">
              <label>{{ t('sales.peakRevenue') }}</label>
              <div class="value">¥{{ fmt(salesSummary.peakRevenue) }}</div>
            </div>
          </div>
          <div class="table-wrap">
            <table class="report-table">
              <thead><tr><th>{{ t('sales.date') }}</th><th class="num">{{ t('sales.orders') }}</th><th class="num">{{ t('sales.revenue') }}</th></tr></thead>
              <tbody>
                <tr v-for="(label, idx) in reportData.labels" :key="label">
                  <td>{{ label }}</td>
                  <td class="num">{{ reportData.counts[idx] }}</td>
                  <td class="num mono">¥{{ fmt(reportData.values[idx]) }}</td>
                </tr>
              </tbody>
              <tfoot v-if="reportData.labels && reportData.labels.length > 0">
                <tr>
                  <td class="left bold">{{ t('report.total') }}</td>
                  <td class="num bold">{{ salesSummary.totalOrders }}</td>
                  <td class="num mono bold">¥{{ fmt(salesSummary.totalRevenue) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>
          <div class="panel">
            <h4 class="panel-title">
              <svg viewBox="0 0 20 20" width="16" height="16"><path d="M3 20h2V10H3v10zm6 0h2V4H9v16zm6 0h2v-7h-2v7zm6 0h2V7h-2v13z" fill="currentColor"/></svg>
              {{ t('sales.insightTitle') }}
            </h4>
            <div class="insight-list">
              <div class="insight-item"><span class="insight-dot success"></span><span>{{ t('sales.insightOrders') }} <b>{{ salesSummary.totalOrders }}</b></span></div>
              <div class="insight-item"><span class="insight-dot primary"></span><span>{{ t('sales.insightRevenue') }} <b>¥{{ fmt(salesSummary.totalRevenue) }}</b></span></div>
              <div class="insight-item"><span class="insight-dot info"></span><span>{{ t('sales.insightAverage') }} <b>¥{{ fmt(salesSummary.avgValue) }}</b></span></div>
              <div class="insight-item"><span class="insight-dot warning"></span><span>{{ t('sales.insightPeak') }} <b>{{ salesSummary.peakDate }}</b></span></div>
            </div>
          </div>
        </div>

        <!-- Delivery Analysis View -->
        <div v-else-if="activeReport.id === 2" class="data-view">
          <div class="kpi-row-4">
            <div class="kpi-card">
              <label>{{ t('delivery.total') }}</label>
              <div class="value">{{ reportData.total }}</div>
            </div>
            <div class="kpi-card success">
              <label>{{ t('delivery.completed') }}</label>
              <div class="value">{{ reportData.completed }}</div>
            </div>
            <div class="kpi-card warn">
              <label>{{ t('delivery.pending') }}</label>
              <div class="value">{{ reportData.pending }}</div>
            </div>
            <div class="kpi-card info">
              <label>{{ t('delivery.completionRate') }}</label>
              <div class="value">{{ reportData.completionRate.toFixed(1) }}%</div>
            </div>
          </div>
          <div class="kpi-row-2">
            <div class="kpi-card success">
              <label>{{ t('delivery.onTime') }}</label>
              <div class="value">{{ reportData.onTime ?? 0 }}</div>
            </div>
            <div class="kpi-card info">
              <label>{{ t('delivery.onTimeRate') }}</label>
              <div class="value">{{ (reportData.onTimeRate ?? 0).toFixed(1) }}%</div>
            </div>
          </div>

          <div class="overview-grid">
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><path d="M10 1a9 9 0 1 0 0 18 9 9 0 0 0 0-18zm0 2v7l5 5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
                {{ t('delivery.statusTitle') }}
              </h4>
              <div class="status-bars">
                <div v-for="s in reportData.statusBreakdown" :key="s.status" class="status-bar-item">
                  <div class="sb-header"><span class="sb-label">{{ s.label }}</span><span class="sb-amount">{{ s.count }}</span></div>
                  <div class="sb-track"><div class="sb-fill delivery-status" :style="{ width: s.percentage + '%' }"></div></div>
                  <span class="sb-meta">{{ s.percentage.toFixed(1) }}%</span>
                </div>
              </div>
            </div>
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><path d="M3 17l4-6 3 4 4-7 3 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                {{ t('delivery.trendTitle') }}
              </h4>
              <div class="table-wrap">
                <table class="report-table">
                  <thead><tr><th>{{ t('delivery.month') }}</th><th class="num">{{ t('delivery.count') }}</th></tr></thead>
                  <tbody>
                    <tr v-if="!reportData.monthlyTrend || reportData.monthlyTrend.length === 0">
                      <td colspan="2" class="center muted">{{ t('report.noData') }}</td>
                    </tr>
                    <tr v-for="m in reportData.monthlyTrend" :key="m.month">
                      <td>{{ formatMonth(m.month) }}</td>
                      <td class="num">{{ m.count }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Financial Summary — Overview Mode -->
        <div v-else-if="activeReport.id === 3 && finMode === 'overview'" class="data-view">
          <!-- KPI Row -->
          <div class="kpi-row-6">
            <div class="kpi-card primary">
              <label>Total Invoiced</label>
              <div class="value">¥{{ fmt(reportData.totalInvoiced) }}</div>
              <span class="kpi-sub">{{ reportData.invoiceCount }} invoices</span>
            </div>
            <div class="kpi-card danger">
              <label>Outstanding AR</label>
              <div class="value">¥{{ fmt(reportData.openReceivables) }}</div>
              <span class="kpi-sub">Uncollected</span>
            </div>
            <div class="kpi-card success">
              <label>Collected</label>
              <div class="value">¥{{ fmt(reportData.collectedAmount) }}</div>
              <span class="kpi-sub">All-time receipts</span>
            </div>
            <div class="kpi-card info">
              <label>Collection Rate</label>
              <div class="value">{{ reportData.collectionRate.toFixed(1) }}%</div>
              <span class="kpi-sub">Recovery ratio</span>
            </div>
            <div class="kpi-card warn">
              <label>Overdue Amount</label>
              <div class="value">¥{{ fmt(reportData.overdueAmount) }}</div>
              <span class="kpi-sub">Past due date</span>
            </div>
            <div class="kpi-card">
              <label>Avg Days to Collect</label>
              <div class="value">{{ reportData.avgDaysToCollect.toFixed(0) }}</div>
              <span class="kpi-sub">Days (DSO)</span>
            </div>
          </div>

          <div class="overview-grid">
            <!-- Invoice Status Distribution -->
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><path d="M10 1a9 9 0 1 0 0 18 9 9 0 0 0 0-18zm0 2v7l5 5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
                Invoice Status Distribution
              </h4>
              <div class="status-bars">
                <div v-for="s in reportData.statusDistribution" :key="s.status" class="status-bar-item">
                  <div class="sb-header">
                    <span class="sb-label">{{ s.label }}</span>
                    <span class="sb-amount">¥{{ fmt(s.amount) }}</span>
                  </div>
                  <div class="sb-track">
                    <div class="sb-fill" :class="statusClass(s.status)" :style="{ width: s.percentage + '%' }"></div>
                  </div>
                  <span class="sb-meta">{{ s.count }} invoices · {{ s.percentage.toFixed(1) }}%</span>
                </div>
              </div>
            </div>

            <!-- AR Aging -->
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 5v5l3 2" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
                AR Aging Analysis
              </h4>
              <div class="aging-list">
                <div v-for="a in reportData.agingSummary" :key="a.bucket" class="aging-item">
                  <div class="aging-info">
                    <span class="aging-bucket">{{ a.bucket }}</span>
                    <span class="aging-amount">¥{{ fmt(a.amount) }}</span>
                  </div>
                  <div class="aging-bar-track">
                    <div class="aging-bar-fill" :class="a.color" :style="{ width: agingPct(a.amount) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Top 5 Outstanding Customers -->
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><circle cx="10" cy="7" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M3 18c0-3.8 3.1-7 7-7s7 3.2 7 7" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
                Top 5 Outstanding Customers
              </h4>
              <div v-if="reportData.topCustomers && reportData.topCustomers.length > 0" class="top-customer-list">
                <div v-for="(c, idx) in reportData.topCustomers" :key="c.bpId" class="tc-item">
                  <div class="tc-rank" :class="'rank-' + (idx + 1)">{{ idx + 1 }}</div>
                  <div class="tc-info">
                    <span class="tc-name">{{ c.bpName }}</span>
                    <span class="tc-id">{{ c.bpId }}</span>
                  </div>
                  <div class="tc-amount danger-text">¥{{ fmt(c.outstanding) }}</div>
                </div>
              </div>
              <div v-else class="empty-mini">No outstanding receivables</div>
            </div>

            <!-- Monthly Collection Trend -->
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><path d="M3 17l4-6 3 4 4-7 3 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                Collection Trend (6 Months)
              </h4>
              <div v-if="reportData.collectionTrend && reportData.collectionTrend.length > 0" class="trend-chart">
                <div class="trend-bars">
                  <div v-for="t in reportData.collectionTrend" :key="t.month" class="trend-col">
                    <div class="trend-bar" :style="{ height: trendBarHeight(t.amount) + 'px' }">
                      <span class="trend-val" v-if="t.amount > 0">¥{{ fmt(t.amount) }}</span>
                    </div>
                    <span class="trend-month">{{ formatMonth(t.month) }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="empty-mini">No collection records in the past 6 months</div>
            </div>
          </div>
        </div>

        <!-- Financial Summary — Statement Mode -->
        <div v-else-if="activeReport.id === 3 && finMode === 'statement'" class="data-view statement-view">
          <!-- Report header -->
          <div class="stmt-header">
            <div class="stmt-title-block">
              <h2 class="stmt-title">Accounts Receivable Report</h2>
              <p class="stmt-period">As of {{ todayStr }}</p>
            </div>
            <div class="stmt-stamp">HAKIMI ERP · Finance Department</div>
          </div>

          <!-- Section 1: AR by Customer -->
          <div class="stmt-section">
            <h3 class="stmt-section-title">I. Accounts Receivable Summary by Customer</h3>
            <table class="stmt-table">
              <thead>
                <tr>
                  <th class="left">Customer</th>
                  <th class="left">BP ID</th>
                  <th class="num">Beginning Balance</th>
                  <th class="num">This Period Invoiced</th>
                  <th class="num">This Period Collected</th>
                  <th class="num">Ending Balance</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in reportData.arByCustomer" :key="row.bpId">
                  <td class="left">{{ row.bpName }}</td>
                  <td class="left mono-sm">{{ row.bpId }}</td>
                  <td class="num mono">¥{{ fmt(row.beginningBalance) }}</td>
                  <td class="num mono">¥{{ fmt(row.invoicedThisPeriod) }}</td>
                  <td class="num mono">¥{{ fmt(row.collectedThisPeriod) }}</td>
                  <td class="num mono bold" :class="{ 'danger-text': row.endingBalance > 0 }">¥{{ fmt(row.endingBalance) }}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="2" class="left bold">Total</td>
                  <td class="num mono bold">¥{{ fmt(sumByKey(reportData.arByCustomer, 'beginningBalance')) }}</td>
                  <td class="num mono bold">¥{{ fmt(sumByKey(reportData.arByCustomer, 'invoicedThisPeriod')) }}</td>
                  <td class="num mono bold">¥{{ fmt(sumByKey(reportData.arByCustomer, 'collectedThisPeriod')) }}</td>
                  <td class="num mono bold" :class="{ 'danger-text': sumByKey(reportData.arByCustomer, 'endingBalance') > 0 }">¥{{ fmt(sumByKey(reportData.arByCustomer, 'endingBalance')) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- Section 2: Receipt Ledger -->
          <div class="stmt-section">
            <h3 class="stmt-section-title">II. Receipt Ledger</h3>
            <table class="stmt-table">
              <thead>
                <tr>
                  <th class="left">Receipt No.</th>
                  <th class="left">Invoice No.</th>
                  <th class="left">Customer</th>
                  <th class="left">Date</th>
                  <th class="left">Payment Method</th>
                  <th class="left">Reference</th>
                  <th class="num">Amount</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="reportData.receiptLedger && reportData.receiptLedger.length === 0">
                  <td colspan="7" class="center muted">No receipt records found</td>
                </tr>
                <tr v-for="r in reportData.receiptLedger" :key="r.receiptId">
                  <td class="left mono-sm">{{ r.receiptId }}</td>
                  <td class="left mono-sm">{{ r.invoiceId }}</td>
                  <td class="left">{{ r.bpName }}</td>
                  <td class="left mono-sm">{{ r.receiptDate }}</td>
                  <td class="left">{{ paymentMethodLabel(r.paymentMethod) }}</td>
                  <td class="left mono-sm">{{ r.referenceNo || '—' }}</td>
                  <td class="num mono">¥{{ fmt(r.amount) }}</td>
                </tr>
              </tbody>
              <tfoot v-if="reportData.receiptLedger && reportData.receiptLedger.length > 0">
                <tr>
                  <td colspan="6" class="left bold">Total Receipts</td>
                  <td class="num mono bold">¥{{ fmt(reportData.receiptLedger.reduce((s, r) => s + r.amount, 0)) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- Section 3: Invoice Summary by Status -->
          <div class="stmt-section">
            <h3 class="stmt-section-title">III. Invoice Summary by Status</h3>
            <table class="stmt-table">
              <thead>
                <tr>
                  <th class="left">Status</th>
                  <th class="num">Count</th>
                  <th class="num">Amount</th>
                  <th class="num">Percentage</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in reportData.invoiceSummary" :key="s.status">
                  <td class="left">
                    <span class="status-tag" :class="statusClass(s.status)">{{ s.label }}</span>
                  </td>
                  <td class="num">{{ s.count }}</td>
                  <td class="num mono">¥{{ fmt(s.amount) }}</td>
                  <td class="num">{{ s.percentage.toFixed(1) }}%</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td class="left bold">Total</td>
                  <td class="num bold">{{ reportData.invoiceSummary.reduce((s, r) => s + r.count, 0) }}</td>
                  <td class="num mono bold">¥{{ fmt(reportData.invoiceSummary.reduce((s, r) => s + r.amount, 0)) }}</td>
                  <td class="num bold">100.0%</td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- Section 4: Overdue Analysis -->
          <div class="stmt-section">
            <h3 class="stmt-section-title">IV. Overdue Receivables Analysis</h3>
            <table class="stmt-table">
              <thead>
                <tr>
                  <th class="left">Invoice No.</th>
                  <th class="left">Customer</th>
                  <th class="left">Invoice Date</th>
                  <th class="left">Due Date</th>
                  <th class="num">Days Overdue</th>
                  <th class="num">Outstanding</th>
                  <th class="center">Risk Level</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="reportData.overdueInvoices && reportData.overdueInvoices.length === 0">
                  <td colspan="7" class="center muted">No overdue receivables</td>
                </tr>
                <tr v-for="o in reportData.overdueInvoices" :key="o.invoiceId" class="risk-row">
                  <td class="left mono-sm">{{ o.invoiceId }}</td>
                  <td class="left">{{ o.bpName }}</td>
                  <td class="left mono-sm">{{ o.invoiceDate }}</td>
                  <td class="left mono-sm">{{ o.dueDate }}</td>
                  <td class="num" :class="{ 'danger-text': o.daysOverdue > 90 }">{{ o.daysOverdue }}</td>
                  <td class="num mono">¥{{ fmt(o.outstanding) }}</td>
                  <td class="center"><span class="risk-tag" :class="riskClass(o.riskLevel)">{{ o.riskLevel }}</span></td>
                </tr>
              </tbody>
              <tfoot v-if="reportData.overdueInvoices && reportData.overdueInvoices.length > 0">
                <tr>
                  <td colspan="5" class="left bold">Total Overdue</td>
                  <td class="num mono bold danger-text">¥{{ fmt(reportData.overdueInvoices.reduce((s, r) => s + r.outstanding, 0)) }}</td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>

          <!-- Statement footer -->
          <div class="stmt-footer">
            <p>This report is generated by HAKIMI ERP System on {{ todayStr }}.</p>
            <p>All amounts are expressed in CNY unless otherwise stated.</p>
          </div>
        </div>

        <!-- Customer Analysis View -->
        <div v-else-if="activeReport.id === 4" class="data-view">
          <div class="kpi-row-4">
            <div class="kpi-card">
              <label>{{ t('customer.total') }}</label>
              <div class="value">{{ reportData.totalCustomers }}</div>
            </div>
            <div class="kpi-card success">
              <label>{{ t('customer.active') }}</label>
              <div class="value">{{ reportData.activeCustomers }}</div>
            </div>
            <div class="kpi-card danger">
              <label>{{ t('customer.blocked') }}</label>
              <div class="value">{{ reportData.blockedCustomers }}</div>
            </div>
            <div class="kpi-card info">
              <label>{{ t('customer.activeRate') }}</label>
              <div class="value">{{ customerActiveRate.toFixed(1) }}%</div>
            </div>
          </div>

          <div class="overview-grid">
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><circle cx="10" cy="7" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M3 18c0-3.8 3.1-7 7-7s7 3.2 7 7" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
                {{ t('customer.topTitle') }}
              </h4>
              <div class="table-wrap">
                <table class="report-table">
                  <thead><tr><th>{{ t('customer.customer') }}</th><th>BP ID</th><th class="num">{{ t('customer.orders') }}</th><th class="num">{{ t('customer.revenue') }}</th><th class="num">{{ t('report.share') }}</th></tr></thead>
                  <tbody>
                    <tr v-if="!reportData.topCustomers || reportData.topCustomers.length === 0">
                      <td colspan="5" class="center muted">{{ t('report.noData') }}</td>
                    </tr>
                    <tr v-for="c in reportData.topCustomers" :key="c.bpId">
                      <td>{{ c.bpName }}</td>
                      <td class="mono-sm">{{ c.bpId }}</td>
                      <td class="num">{{ c.orderCount }}</td>
                      <td class="num mono">¥{{ fmt(c.revenue) }}</td>
                      <td class="num">{{ customerShare(c.revenue).toFixed(1) }}%</td>
                    </tr>
                  </tbody>
                  <tfoot v-if="reportData.topCustomers && reportData.topCustomers.length > 0">
                    <tr>
                      <td class="left bold">{{ t('report.total') }}</td>
                      <td></td>
                      <td class="num bold">{{ customerOrderTotal }}</td>
                      <td class="num mono bold">¥{{ fmt(customerRevenueTotal) }}</td>
                      <td class="num bold">100.0%</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><path d="M3 17l4-6 3 4 4-7 3 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                {{ t('customer.newTitle') }}
              </h4>
              <div class="table-wrap">
                <table class="report-table">
                  <thead><tr><th>{{ t('customer.month') }}</th><th class="num">{{ t('customer.newCount') }}</th></tr></thead>
                  <tbody>
                    <tr v-if="!reportData.newCustomersTrend || reportData.newCustomersTrend.length === 0">
                      <td colspan="2" class="center muted">{{ t('report.noData') }}</td>
                    </tr>
                    <tr v-for="n in reportData.newCustomersTrend" :key="n.month">
                      <td>{{ formatMonth(n.month) }}</td>
                      <td class="num">{{ n.count }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Inventory Turnover View -->
        <div v-else-if="activeReport.id === 5" class="data-view">
          <div class="kpi-row-4">
            <div class="kpi-card">
              <label>{{ t('inventory.materials') }}</label>
              <div class="value">{{ reportData.materialCount }}</div>
            </div>
            <div class="kpi-card info">
              <label>{{ t('inventory.totalStock') }}</label>
              <div class="value">{{ reportData.totalStock }}</div>
            </div>
            <div class="kpi-card warn">
              <label>{{ t('inventory.lowStock') }}</label>
              <div class="value">{{ reportData.lowStockCount }}</div>
            </div>
            <div class="kpi-card success">
              <label>{{ t('inventory.categoryCount') }}</label>
              <div class="value">{{ inventoryCategoryCount }}</div>
            </div>
          </div>

          <div class="overview-grid">
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><path d="M21 16V8a2 2 0 0 0-1-1.73L13 2.27a2 2 0 0 0-2 0L4 6.27A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>
                {{ t('inventory.turnoverTitle') }}
              </h4>
              <div class="table-wrap">
                <table class="report-table">
                  <thead><tr><th>{{ t('inventory.material') }}</th><th>{{ t('inventory.category') }}</th><th class="num">{{ t('inventory.stock') }}</th><th class="num">{{ t('inventory.sold') }}</th><th class="num">{{ t('inventory.turnover') }}</th><th class="num">{{ t('report.status') }}</th></tr></thead>
                  <tbody>
                    <tr v-if="!reportData.inventoryTurnover || reportData.inventoryTurnover.length === 0">
                      <td colspan="6" class="center muted">{{ t('report.noData') }}</td>
                    </tr>
                    <tr v-for="m in reportData.inventoryTurnover" :key="m.materialId">
                      <td>{{ m.materialName }}</td>
                      <td>{{ m.category }}</td>
                      <td class="num">{{ m.stock }}</td>
                      <td class="num">{{ m.soldQuantity }}</td>
                      <td class="num">{{ m.turnoverRate.toFixed(2) }}</td>
                      <td class="center"><span class="status-tag" :class="m.stock < 10 ? 'st-void' : 'st-cleared'">{{ m.stock < 10 ? t('report.low') : t('report.healthy') }}</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><path d="M3 20h2V10H3v10zm6 0h2V4H9v16zm6 0h2v-7h-2v7zm6 0h2V7h-2v13z" fill="currentColor"/></svg>
                {{ t('inventory.categoryTitle') }}
              </h4>
              <div class="status-bars">
                <div v-for="c in reportData.categorySummary" :key="c.category" class="status-bar-item">
                  <div class="sb-header"><span class="sb-label">{{ c.category }}</span><span class="sb-amount">{{ c.stock }}</span></div>
                  <div class="sb-track"><div class="sb-fill inventory-category" :style="{ width: categoryShare(c.stock).toFixed(1) + '%' }"></div></div>
                  <span class="sb-meta">{{ categoryShare(c.stock).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pricing Conditions View -->
        <div v-else-if="activeReport.id === 6" class="data-view">
          <div class="kpi-row-4">
            <div class="kpi-card">
              <label>{{ t('pricing.total') }}</label>
              <div class="value">{{ reportData.totalConditions }}</div>
            </div>
            <div class="kpi-card success">
              <label>{{ t('pricing.active') }}</label>
              <div class="value">{{ reportData.activeConditions }}</div>
            </div>
            <div class="kpi-card info">
              <label>{{ t('pricing.types') }}</label>
              <div class="value">{{ reportData.typeCount }}</div>
            </div>
            <div class="kpi-card warn">
              <label>{{ t('pricing.activeRate') }}</label>
              <div class="value">{{ pricingActiveRate.toFixed(1) }}%</div>
            </div>
          </div>

          <div class="overview-grid">
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><rect x="2" y="3" width="16" height="14" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5 7h10M5 10h10M5 13h7" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>
                {{ t('pricing.typeTitle') }}
              </h4>
              <div class="table-wrap">
                <table class="report-table">
                  <thead><tr><th>{{ t('pricing.type') }}</th><th class="num">{{ t('pricing.count') }}</th><th class="num">{{ t('pricing.avgRate') }}</th><th class="num">{{ t('pricing.avgAmount') }}</th></tr></thead>
                  <tbody>
                    <tr v-if="!reportData.byType || reportData.byType.length === 0">
                      <td colspan="4" class="center muted">{{ t('report.noData') }}</td>
                    </tr>
                    <tr v-for="p in reportData.byType" :key="p.conditionType">
                      <td>{{ p.conditionType }}</td>
                      <td class="num">{{ p.count }}</td>
                      <td class="num">{{ p.averageRate.toFixed(2) }}</td>
                      <td class="num mono">¥{{ fmt(p.averageAmount) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.56 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>
                {{ t('pricing.topTitle') }}
              </h4>
              <div class="table-wrap">
                <table class="report-table">
                  <thead><tr><th>{{ t('pricing.condition') }}</th><th>{{ t('pricing.type') }}</th><th class="num">{{ t('pricing.avgRate') }}</th><th>{{ t('pricing.status') }}</th><th class="num">{{ t('pricing.amount') }}</th></tr></thead>
                  <tbody>
                    <tr v-if="!reportData.topConditions || reportData.topConditions.length === 0">
                      <td colspan="5" class="center muted">{{ t('report.noData') }}</td>
                    </tr>
                    <tr v-for="c in reportData.topConditions" :key="c.conditionId">
                      <td>{{ c.conditionName }}</td>
                      <td>{{ c.conditionType }}</td>
                      <td class="num">{{ (c.rate ?? 0).toFixed(2) }}</td>
                      <td>{{ c.status }}</td>
                      <td class="num mono">¥{{ fmt(c.amount) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Tax & Compliance View -->
        <div v-else-if="activeReport.id === 7" class="data-view">
          <div class="kpi-row-4">
            <div class="kpi-card">
              <label>{{ t('tax.totalTax') }}</label>
              <div class="value">¥{{ fmt(reportData.totalTax) }}</div>
            </div>
            <div class="kpi-card info">
              <label>{{ t('tax.invoicedAmount') }}</label>
              <div class="value">¥{{ fmt(reportData.invoicedAmount) }}</div>
            </div>
            <div class="kpi-card success">
              <label>{{ t('tax.invoices') }}</label>
              <div class="value">{{ reportData.invoiceCount }}</div>
            </div>
            <div class="kpi-card warn">
              <label>{{ t('tax.effectiveRate') }}</label>
              <div class="value">{{ reportData.effectiveTaxRate.toFixed(1) }}%</div>
            </div>
          </div>

          <div class="overview-grid">
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><rect x="3" y="3" width="14" height="14" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M3 9h14M9 3v14" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>
                {{ t('tax.monthlyTitle') }}
              </h4>
              <div class="table-wrap">
                <table class="report-table">
                  <thead><tr><th>{{ t('tax.month') }}</th><th class="num">{{ t('tax.taxAmount') }}</th><th class="num">{{ t('tax.invoiceCount') }}</th><th class="num">{{ t('report.share') }}</th></tr></thead>
                  <tbody>
                    <tr v-if="!reportData.taxByMonth || reportData.taxByMonth.length === 0">
                      <td colspan="4" class="center muted">{{ t('report.noData') }}</td>
                    </tr>
                    <tr v-for="t in reportData.taxByMonth" :key="t.month">
                      <td>{{ formatMonth(t.month) }}</td>
                      <td class="num mono">¥{{ fmt(t.taxAmount) }}</td>
                      <td class="num">{{ t.invoiceCount }}</td>
                      <td class="num">{{ taxShare(t.taxAmount).toFixed(1) }}%</td>
                    </tr>
                  </tbody>
                  <tfoot v-if="reportData.taxByMonth && reportData.taxByMonth.length > 0">
                    <tr>
                      <td class="left bold">{{ t('report.total') }}</td>
                      <td class="num mono bold">¥{{ fmt(taxTotal) }}</td>
                      <td class="num bold">{{ taxInvoiceTotal }}</td>
                      <td class="num bold">100.0%</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><path d="M10 1a9 9 0 1 0 0 18 9 9 0 0 0 0-18zm0 2v7l5 5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
                {{ t('tax.complianceTitle') }}
              </h4>
              <div class="insight-list">
                <div class="insight-item"><span class="insight-dot success"></span><span>{{ t('tax.invoiceBase') }} <b>¥{{ fmt(reportData.invoicedAmount) }}</b></span></div>
                <div class="insight-item"><span class="insight-dot info"></span><span>{{ t('tax.effectiveRate') }} <b>{{ reportData.effectiveTaxRate.toFixed(1) }}%</b></span></div>
                <div class="insight-item"><span class="insight-dot warning"></span><span>{{ t('tax.auditHint') }}</span></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quotation Conversion View -->
        <div v-else-if="activeReport.id === 8" class="data-view">
          <div class="kpi-row-4">
            <div class="kpi-card">
              <label>{{ t('quotation.total') }}</label>
              <div class="value">{{ reportData.totalQuotations }}</div>
            </div>
            <div class="kpi-card success">
              <label>{{ t('quotation.converted') }}</label>
              <div class="value">{{ reportData.convertedQuotations }}</div>
            </div>
            <div class="kpi-card info">
              <label>{{ t('quotation.open') }}</label>
              <div class="value">{{ reportData.openQuotations }}</div>
            </div>
            <div class="kpi-card warn">
              <label>{{ t('quotation.conversionRate') }}</label>
              <div class="value">{{ reportData.conversionRate.toFixed(1) }}%</div>
            </div>
          </div>

          <div class="overview-grid">
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><path d="M3 17l4-6 3 4 4-7 3 5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                {{ t('quotation.trendTitle') }}
              </h4>
              <div class="table-wrap">
                <table class="report-table">
                  <thead><tr><th>{{ t('quotation.month') }}</th><th class="num">{{ t('quotation.quotations') }}</th><th class="num">{{ t('quotation.orders') }}</th><th class="num">{{ t('quotation.conversion') }}</th></tr></thead>
                  <tbody>
                    <tr v-if="!reportData.monthlyTrend || reportData.monthlyTrend.length === 0">
                      <td colspan="4" class="center muted">{{ t('report.noData') }}</td>
                    </tr>
                    <tr v-for="m in reportData.monthlyTrend" :key="m.month">
                      <td>{{ formatMonth(m.month) }}</td>
                      <td class="num">{{ m.quotations }}</td>
                      <td class="num">{{ m.orders }}</td>
                      <td class="num">{{ m.conversionRate.toFixed(1) }}%</td>
                    </tr>
                  </tbody>
                  <tfoot v-if="reportData.monthlyTrend && reportData.monthlyTrend.length > 0">
                    <tr>
                      <td class="left bold">{{ t('report.total') }}</td>
                      <td class="num bold">{{ quotationTotal }}</td>
                      <td class="num bold">{{ convertedTotal }}</td>
                      <td class="num bold">{{ reportData.conversionRate.toFixed(1) }}%</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
            <div class="panel">
              <h4 class="panel-title">
                <svg viewBox="0 0 20 20" width="16" height="16"><circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10 5v5l3 2" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
                {{ t('quotation.pipelineTitle') }}
              </h4>
              <div class="insight-list">
                <div class="insight-item"><span class="insight-dot primary"></span><span>{{ t('quotation.pipelineVolume') }} <b>{{ reportData.totalQuotations }}</b></span></div>
                <div class="insight-item"><span class="insight-dot success"></span><span>{{ t('quotation.won') }} <b>{{ reportData.convertedQuotations }}</b></span></div>
                <div class="insight-item"><span class="insight-dot info"></span><span>{{ t('quotation.open') }} <b>{{ reportData.openQuotations }}</b></span></div>
                <div class="insight-item"><span class="insight-dot warning"></span><span>{{ t('quotation.healthHint') }}</span></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Generic View for others -->
        <div v-else class="empty-result">
          <svg viewBox="0 0 24 24" width="64" height="64" opacity="0.1"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" fill="currentColor"/><path d="M13 2v7h7" fill="none" stroke="currentColor" stroke-width="2"/></svg>
          <p>Report generation completed. Detailed visualization for this report type is coming soon.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { alert } from '@/utils/toast'
import { useI18n } from '@/i18n'
import {
  fetchSalesPerformance,
  fetchFinancialDetail,
  fetchDeliveryStats,
  fetchCustomerAnalysis,
  fetchInventoryTurnover,
  fetchPricingConditionsReport,
  fetchTaxComplianceReport,
  fetchQuotationConversionReport,
} from '@/api/modules/report'

const { t } = useI18n()

interface R{id:number;title:string;desc:string;category:string;updated:string;icon:string}
const reports:R[]=[
  {id:1,title:"Sales Performance Report",desc:"Monthly sales revenue, order volume, and customer acquisition analysis.",category:"Sales",updated:"2026-07-28",icon:'<svg viewBox="0 0 24 24" width="28" height="28"><path d="M3 20h2V10H3v10zm6 0h2V4H9v16zm6 0h2v-7h-2v7zm6 0h2V7h-2v13z" fill="none" stroke="#436850" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'},
  {id:2,title:"Delivery Analysis Report",desc:"On-time delivery rate, logistics cost breakdown, and shipping trends.",category:"Delivery",updated:"2026-07-25",icon:'<svg viewBox="0 0 24 24" width="28" height="28"><rect x="1" y="3" width="15" height="11" rx="1" fill="none" stroke="#436850" stroke-width="1.8"/><path d="M16 8h4l3 4v3h-3a2 2 0 0 1-4 0" fill="none" stroke="#436850" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="7" cy="18" r="2" fill="none" stroke="#436850" stroke-width="1.5"/><circle cx="18" cy="18" r="2" fill="none" stroke="#436850" stroke-width="1.5"/></svg>'},
  {id:3,title:"Financial Summary Report",desc:"Revenue, profit margin, invoice aging, and cash flow overview.",category:"Finance",updated:"2026-07-22",icon:'<svg viewBox="0 0 24 24" width="28" height="28"><rect x="2" y="4" width="20" height="16" rx="2" fill="none" stroke="#436850" stroke-width="1.8"/><path d="M7 15l3-3 2 2 4-4" fill="none" stroke="#436850" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="17" cy="10" r="1.5" fill="#436850"/></svg>'},
  {id:4,title:"Customer Analysis Report",desc:"Customer segmentation, retention rates, and purchasing behavior trends.",category:"Customer",updated:"2026-07-20",icon:'<svg viewBox="0 0 24 24" width="28" height="28"><circle cx="9" cy="7" r="4" fill="none" stroke="#436850" stroke-width="1.8"/><path d="M1 21c0-4.4 3.6-8 8-8s8 3.6 8 8" fill="none" stroke="#436850" stroke-width="1.8" stroke-linecap="round"/><circle cx="18" cy="6" r="3" fill="none" stroke="#436850" stroke-width="1.5"/><path d="M23 16c0-2.2-1.8-4-4-4" fill="none" stroke="#436850" stroke-width="1.5" stroke-linecap="round"/></svg>'},
  {id:5,title:"Inventory Turnover Report",desc:"Stock levels, turnover rates, and material movement analysis.",category:"Inventory",updated:"2026-07-18",icon:'<svg viewBox="0 0 24 24" width="28" height="28"><path d="M21 16V8a2 2 0 0 0-1-1.73L13 2.27a2 2 0 0 0-2 0L4 6.27A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" fill="none" stroke="#436850" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 12l7-4M12 12v9M12 12L5 8" fill="none" stroke="#436850" stroke-width="1.2" stroke-linecap="round"/></svg>'},
  {id:6,title:"Pricing Conditions Report",desc:"Discount distribution, margin analysis, and pricing strategy overview.",category:"Pricing",updated:"2026-07-15",icon:'<svg viewBox="0 0 24 24" width="28" height="28"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.56 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z" fill="none" stroke="#436850" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'},
  {id:7,title:"Tax & Compliance Report",desc:"Tax summary, compliance status, and regulatory audit trail.",category:"Finance",updated:"2026-07-12",icon:'<svg viewBox="0 0 24 24" width="28" height="28"><rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="#436850" stroke-width="1.8"/><path d="M3 9h18M9 3v18" fill="none" stroke="#436850" stroke-width="1.2"/></svg>'},
  {id:8,title:"Quotation Conversion Report",desc:"Quotation-to-order conversion rates, win/loss analysis, and pipeline health.",category:"Sales",updated:"2026-07-10",icon:'<svg viewBox="0 0 24 24" width="28" height="28"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" fill="none" stroke="#436850" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" fill="none" stroke="#436850" stroke-width="1.5" stroke-linecap="round"/></svg>'},
]

const reportTitleKeys: Record<number, string> = {
  1: 'sales.title',
  2: 'delivery.title',
  3: 'report.financialTitle',
  4: 'customer.title',
  5: 'inventory.title',
  6: 'pricing.title',
  7: 'tax.title',
  8: 'quotation.title',
}

const reportDescKeys: Record<number, string> = {
  1: 'sales.desc',
  2: 'delivery.desc',
  3: 'report.financialDesc',
  4: 'customer.desc',
  5: 'inventory.desc',
  6: 'pricing.desc',
  7: 'tax.desc',
  8: 'quotation.desc',
}

function reportTitle(id: number): string {
  return t(reportTitleKeys[id] || 'report.title')
}

function reportDesc(id: number): string {
  return t(reportDescKeys[id] || 'report.subtitle')
}

const activeReport = ref<R | null>(null)
const reportData = ref<any>(null)
const loading = ref(false)
const finMode = ref<'overview' | 'statement'>('overview')
const salesDays = ref(30)

async function runReport(r: R) {
  activeReport.value = r
  finMode.value = 'overview'
  await refreshReport()
}

async function refreshReport() {
  if (!activeReport.value) return
  loading.value = true
  reportData.value = null
  try {
    if (activeReport.value.id === 1) {
      reportData.value = await fetchSalesPerformance({ days: salesDays.value })
    } else if (activeReport.value.id === 2) {
      reportData.value = await fetchDeliveryStats()
    } else if (activeReport.value.id === 3) {
      reportData.value = await fetchFinancialDetail()
    } else if (activeReport.value.id === 4) {
      reportData.value = await fetchCustomerAnalysis()
    } else if (activeReport.value.id === 5) {
      reportData.value = await fetchInventoryTurnover()
    } else if (activeReport.value.id === 6) {
      reportData.value = await fetchPricingConditionsReport()
    } else if (activeReport.value.id === 7) {
      reportData.value = await fetchTaxComplianceReport()
    } else if (activeReport.value.id === 8) {
      reportData.value = await fetchQuotationConversionReport()
    } else {
      await new Promise(resolve => setTimeout(resolve, 800))
      reportData.value = { mock: true }
    }
  } catch (err: any) {
    alert('Failed to generate report: ' + err.message)
  } finally {
    loading.value = false
  }
}

const salesSummary = computed(() => {
  if (!reportData.value || activeReport.value?.id !== 1) {
    return { totalOrders: 0, totalRevenue: 0, avgValue: 0, peakRevenue: 0, peakDate: '', share: (_n: number) => 0 }
  }
  const totalOrders = reportData.value.counts.reduce((a: number, b: number) => a + b, 0)
  const totalRevenue = reportData.value.values.reduce((a: number, b: number) => a + b, 0)
  const peakIndex = reportData.value.values.reduce((best: number, value: number, idx: number, arr: number[]) =>
    value > (arr[best] || 0) ? idx : best, 0)
  return {
    totalOrders,
    totalRevenue,
    avgValue: totalOrders > 0 ? totalRevenue / totalOrders : 0,
    peakRevenue: reportData.value.values[peakIndex] || 0,
    peakDate: reportData.value.labels?.[peakIndex] || '',
    share: (value: number) => totalRevenue > 0 ? (value / totalRevenue) * 100 : 0,
  }
})

const customerActiveRate = computed(() => {
  if (!reportData.value) return 0
  const total = reportData.value.totalCustomers || 0
  return total > 0 ? ((reportData.value.activeCustomers || 0) / total) * 100 : 0
})

const customerRevenueTotal = computed(() => {
  return (reportData.value?.topCustomers || []).reduce((sum: number, row: any) => sum + (row.revenue || 0), 0)
})

const customerOrderTotal = computed(() => {
  return (reportData.value?.topCustomers || []).reduce((sum: number, row: any) => sum + (row.orderCount || 0), 0)
})

function customerShare(revenue: number): number {
  return customerRevenueTotal.value > 0 ? (revenue / customerRevenueTotal.value) * 100 : 0
}

const inventoryCategoryCount = computed(() => (reportData.value?.categorySummary || []).length)

function categoryShare(stock: number): number {
  const total = reportData.value?.totalStock || 0
  return total > 0 ? (stock / total) * 100 : 0
}

const pricingActiveRate = computed(() => {
  const total = reportData.value?.totalConditions || 0
  return total > 0 ? ((reportData.value?.activeConditions || 0) / total) * 100 : 0
})

const taxTotal = computed(() => (reportData.value?.taxByMonth || []).reduce((sum: number, row: any) => sum + (row.taxAmount || 0), 0))

const taxInvoiceTotal = computed(() => (reportData.value?.taxByMonth || []).reduce((sum: number, row: any) => sum + (row.invoiceCount || 0), 0))

function taxShare(amount: number): number {
  return taxTotal.value > 0 ? (amount / taxTotal.value) * 100 : 0
}

const quotationTotal = computed(() => (reportData.value?.monthlyTrend || []).reduce((sum: number, row: any) => sum + (row.quotations || 0), 0))

const convertedTotal = computed(() => (reportData.value?.monthlyTrend || []).reduce((sum: number, row: any) => sum + (row.orders || 0), 0))

// --- Helpers ---
function fmt(n: number): string {
  return (n || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function statusClass(status: string): string {
  const map: Record<string, string> = { CLEARED: 'st-cleared', PARTIAL: 'st-partial', OPEN: 'st-open', VOID: 'st-void' }
  return map[status] || 'st-open'
}

function riskClass(level: string): string {
  const map: Record<string, string> = { High: 'rk-high', Medium: 'rk-medium', Low: 'rk-low' }
  return map[level] || 'rk-low'
}

function paymentMethodLabel(method: string): string {
  const map: Record<string, string> = {
    BANK_TRANSFER: 'Bank Transfer', CASH: 'Cash', CHECK: 'Check',
    CREDIT_CARD: 'Credit Card', WIRE: 'Wire Transfer', ELECTRONIC: 'Electronic Transfer'
  }
  return map[method] || method || '—'
}

function agingPct(amount: number): number {
  if (!reportData.value || !reportData.value.overdueAmount) return 0
  const totalOverdue = reportData.value.agingSummary.reduce((s: number, a: any) => s + a.amount, 0)
  return totalOverdue > 0 ? (amount / totalOverdue) * 100 : 0
}

function trendBarHeight(amount: number): number {
  if (!reportData.value?.collectionTrend) return 0
  const max = Math.max(...reportData.value.collectionTrend.map((t: any) => t.amount), 1)
  return Math.max((amount / max) * 140, 4)
}

function formatMonth(ym: string): string {
  const [y, m] = ym.split('-')
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  return months[parseInt(m) - 1] || m
}

function sumByKey(arr: any[], key: string): number {
  return arr.reduce((s, r) => s + (r[key] || 0), 0)
}

const todayStr = computed(() => {
  const d = new Date()
  return d.toISOString().split('T')[0]
})

function exportData() {
  if (!activeReport.value || !reportData.value) return

  const data = reportData.value
  const id = activeReport.value.id
  const title = reportTitle(id)
  buildExcelExport(id, data, title)
  return

  const escapeCsv = (value: string | number) => {
    const text = String(value ?? '')
    return `"${text.replace(/"/g, '""')}"`
  }
  const section = (heading: string, header: string[], rows: (string | number)[][]) => {
    lines.push('')
    lines.push(heading)
    lines.push(header.map(escapeCsv).join(','))
    rows.forEach((row) => lines.push(row.map(escapeCsv).join(',')))
  }
  const lines: string[] = [
    title,
    `${t('report.asOf')} ${todayStr.value}`,
    t('report.generatedBy'),
    t('report.currencyNote'),
  ]

  if (id === 1) {
    section(t('sales.trendTitle'), [t('sales.date'), t('sales.orders'), t('sales.revenue')], (data.labels || []).map((label: string, idx: number) => [
      label,
      data.counts?.[idx] ?? 0,
      Number(data.values?.[idx] ?? 0).toFixed(2),
    ]))
    section(t('report.total'), [t('sales.totalOrders'), t('sales.totalRevenue'), t('sales.avgOrder')], [[
      salesSummary.value.totalOrders,
      Number(salesSummary.value.totalRevenue).toFixed(2),
      Number(salesSummary.value.avgValue).toFixed(2),
    ]])
  } else if (id === 2) {
    section(t('delivery.title'), [t('report.metric'), t('report.value')], [
      [t('delivery.total'), data.total],
      [t('delivery.completed'), data.completed],
      [t('delivery.pending'), data.pending],
      [t('delivery.completionRate'), `${data.completionRate.toFixed(1)}%`],
      [t('delivery.onTime'), data.onTime ?? 0],
      [t('delivery.onTimeRate'), `${(data.onTimeRate ?? 0).toFixed(1)}%`],
    ])
    section(t('delivery.statusTitle'), [t('delivery.status'), t('delivery.count'), t('delivery.percentage')], (data.statusBreakdown || []).map((row: any) => [
      row.label,
      row.count,
      `${row.percentage.toFixed(1)}%`,
    ]))
  } else if (id === 3) {
    section(t('report.statement'), ['Customer', 'BP ID', 'Beginning Balance', 'Invoiced This Period', 'Collected This Period', 'Ending Balance'], (data.arByCustomer || []).map((row: any) => [
      row.bpName,
      row.bpId,
      Number(row.beginningBalance).toFixed(2),
      Number(row.invoicedThisPeriod).toFixed(2),
      Number(row.collectedThisPeriod).toFixed(2),
      Number(row.endingBalance).toFixed(2),
    ]))
    section(t('report.aging'), ['Invoice', 'Customer', 'Due Date', 'Days Overdue', 'Outstanding', 'Risk'], (data.overdueInvoices || []).map((row: any) => [
      row.invoiceId,
      row.bpName,
      row.dueDate,
      row.daysOverdue,
      Number(row.outstanding).toFixed(2),
      row.riskLevel,
    ]))
  } else if (id === 4) {
    section(t('customer.topTitle'), [t('customer.customer'), 'BP ID', t('customer.orders'), t('customer.revenue')], (data.topCustomers || []).map((row: any) => [
      row.bpName,
      row.bpId,
      row.orderCount,
      Number(row.revenue).toFixed(2),
    ]))
    section(t('customer.newTitle'), [t('customer.month'), t('customer.newCount')], (data.newCustomersTrend || []).map((row: any) => [
      row.month,
      row.count,
    ]))
  } else if (id === 5) {
    section(t('inventory.turnoverTitle'), [t('inventory.material'), t('inventory.category'), t('inventory.stock'), t('inventory.sold'), t('inventory.turnover')], (data.inventoryTurnover || []).map((row: any) => [
      row.materialName,
      row.category,
      row.stock,
      row.soldQuantity,
      Number(row.turnoverRate).toFixed(2),
    ]))
    section(t('inventory.categoryTitle'), [t('inventory.category'), t('inventory.stock')], (data.categorySummary || []).map((row: any) => [
      row.category,
      row.stock,
    ]))
  } else if (id === 6) {
    section(t('pricing.typeTitle'), [t('pricing.type'), t('pricing.count'), t('pricing.avgRate'), t('pricing.avgAmount')], (data.byType || []).map((row: any) => [
      row.conditionType,
      row.count,
      Number(row.averageRate).toFixed(2),
      Number(row.averageAmount).toFixed(2),
    ]))
    section(t('pricing.topTitle'), [t('pricing.condition'), t('pricing.type'), t('pricing.status'), t('pricing.amount')], (data.topConditions || []).map((row: any) => [
      row.conditionName,
      row.conditionType,
      row.status,
      Number(row.amount).toFixed(2),
    ]))
  } else if (id === 7) {
    section(t('tax.monthlyTitle'), [t('tax.month'), t('tax.taxAmount'), t('tax.invoiceCount')], (data.taxByMonth || []).map((row: any) => [
      row.month,
      Number(row.taxAmount).toFixed(2),
      row.invoiceCount,
    ]))
  } else if (id === 8) {
    section(t('quotation.trendTitle'), [t('quotation.month'), t('quotation.quotations'), t('quotation.orders'), t('quotation.conversion')], (data.monthlyTrend || []).map((row: any) => [
      row.month,
      row.quotations,
      row.orders,
      `${Number(row.conversionRate).toFixed(1)}%`,
    ]))
  }

  if (lines.length <= 4) {
    alert(t('report.noExport'))
    return
  }

  const csv = lines.join('\n')
  const blob = new Blob([`\ufeff${csv}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${title.replace(/\s+/g, '-')}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

type ExcelSection = {
  title: string
  headers: string[]
  rows: (string | number)[][]
  totals?: (string | number)[]
  numeric?: boolean[]
}

function buildExcelExport(id: number, data: any, title: string) {
  const sections: ExcelSection[] = []

  if (id === 1) {
    sections.push({
      title: t('sales.trendTitle'),
      headers: [t('sales.date'), t('sales.orders'), t('sales.revenue')],
      numeric: [false, true, true],
      rows: (data.labels || []).map((label: string, idx: number) => [
        label,
        data.counts?.[idx] ?? 0,
        Number(data.values?.[idx] ?? 0).toFixed(2),
      ]),
      totals: [t('report.total'), salesSummary.value.totalOrders, Number(salesSummary.value.totalRevenue).toFixed(2)],
    })
    sections.push({
      title: t('sales.insightTitle'),
      headers: [t('report.metric'), t('report.value')],
      numeric: [false, true],
      rows: [
        [t('sales.totalOrders'), salesSummary.value.totalOrders],
        [t('sales.totalRevenue'), `¥${fmt(salesSummary.value.totalRevenue)}`],
        [t('sales.avgOrder'), `¥${fmt(salesSummary.value.avgValue)}`],
        [t('sales.peakRevenue'), `¥${fmt(salesSummary.value.peakRevenue)}`],
      ],
    })
  } else if (id === 2) {
    sections.push({
      title: t('delivery.title'),
      headers: [t('report.metric'), t('report.value')],
      numeric: [false, true],
      rows: [
        [t('delivery.total'), data.total],
        [t('delivery.completed'), data.completed],
        [t('delivery.pending'), data.pending],
        [t('delivery.completionRate'), `${data.completionRate.toFixed(1)}%`],
        [t('delivery.onTime'), data.onTime ?? 0],
        [t('delivery.onTimeRate'), `${(data.onTimeRate ?? 0).toFixed(1)}%`],
      ],
    })
    sections.push({
      title: t('delivery.statusTitle'),
      headers: [t('delivery.status'), t('delivery.count'), t('delivery.percentage')],
      numeric: [false, true, true],
      rows: (data.statusBreakdown || []).map((row: any) => [row.label, row.count, `${row.percentage.toFixed(1)}%`]),
      totals: [t('report.total'), data.total, '100.0%'],
    })
    sections.push({
      title: t('delivery.trendTitle'),
      headers: [t('delivery.month'), t('delivery.count')],
      numeric: [false, true],
      rows: (data.monthlyTrend || []).map((row: any) => [formatMonth(row.month), row.count]),
    })
  } else if (id === 3) {
    sections.push({
      title: t('report.statement'),
      headers: ['Customer', 'BP ID', 'Beginning Balance', 'Invoiced This Period', 'Collected This Period', 'Ending Balance'],
      numeric: [false, false, true, true, true, true],
      rows: (data.arByCustomer || []).map((row: any) => [
        row.bpName,
        row.bpId,
        Number(row.beginningBalance).toFixed(2),
        Number(row.invoicedThisPeriod).toFixed(2),
        Number(row.collectedThisPeriod).toFixed(2),
        Number(row.endingBalance).toFixed(2),
      ]),
      totals: [t('report.total'), '', Number(sumByKey(data.arByCustomer || [], 'beginningBalance')).toFixed(2), Number(sumByKey(data.arByCustomer || [], 'invoicedThisPeriod')).toFixed(2), Number(sumByKey(data.arByCustomer || [], 'collectedThisPeriod')).toFixed(2), Number(sumByKey(data.arByCustomer || [], 'endingBalance')).toFixed(2)],
    })
    sections.push({
      title: t('report.aging'),
      headers: ['Invoice', 'Customer', 'Due Date', 'Days Overdue', 'Outstanding', 'Risk'],
      numeric: [false, false, false, true, true, false],
      rows: (data.overdueInvoices || []).map((row: any) => [row.invoiceId, row.bpName, row.dueDate, row.daysOverdue, Number(row.outstanding).toFixed(2), row.riskLevel]),
      totals: [t('report.total'), '', '', '', Number((data.overdueInvoices || []).reduce((sum: number, row: any) => sum + (row.outstanding || 0), 0)).toFixed(2), ''],
    })
  } else if (id === 4) {
    sections.push({
      title: t('customer.topTitle'),
      headers: [t('customer.customer'), 'BP ID', t('customer.orders'), t('customer.revenue')],
      numeric: [false, false, true, true],
      rows: (data.topCustomers || []).map((row: any) => [row.bpName, row.bpId, row.orderCount, Number(row.revenue).toFixed(2)]),
      totals: [t('report.total'), '', customerOrderTotal.value, Number(customerRevenueTotal.value).toFixed(2)],
    })
    sections.push({
      title: t('customer.newTitle'),
      headers: [t('customer.month'), t('customer.newCount')],
      numeric: [false, true],
      rows: (data.newCustomersTrend || []).map((row: any) => [formatMonth(row.month), row.count]),
    })
  } else if (id === 5) {
    sections.push({
      title: t('inventory.turnoverTitle'),
      headers: [t('inventory.material'), t('inventory.category'), t('inventory.stock'), t('inventory.sold'), t('inventory.turnover')],
      numeric: [false, false, true, true, true],
      rows: (data.inventoryTurnover || []).map((row: any) => [row.materialName, row.category, row.stock, row.soldQuantity, Number(row.turnoverRate).toFixed(2)]),
      totals: [t('report.total'), '', data.totalStock, (data.inventoryTurnover || []).reduce((sum: number, row: any) => sum + (row.soldQuantity || 0), 0), ''],
    })
    sections.push({
      title: t('inventory.categoryTitle'),
      headers: [t('inventory.category'), t('inventory.stock')],
      numeric: [false, true],
      rows: (data.categorySummary || []).map((row: any) => [row.category, row.stock]),
      totals: [t('report.total'), data.totalStock],
    })
  } else if (id === 6) {
    sections.push({
      title: t('pricing.typeTitle'),
      headers: [t('pricing.type'), t('pricing.count'), t('pricing.avgRate'), t('pricing.avgAmount')],
      numeric: [false, true, true, true],
      rows: (data.byType || []).map((row: any) => [row.conditionType, row.count, Number(row.averageRate).toFixed(2), Number(row.averageAmount).toFixed(2)]),
      totals: [t('report.total'), data.totalConditions, '', ''],
    })
    sections.push({
      title: t('pricing.topTitle'),
      headers: [t('pricing.condition'), t('pricing.type'), t('pricing.status'), t('pricing.amount')],
      numeric: [false, false, false, true],
      rows: (data.topConditions || []).map((row: any) => [row.conditionName, row.conditionType, row.status, Number(row.amount).toFixed(2)]),
    })
  } else if (id === 7) {
    sections.push({
      title: t('tax.monthlyTitle'),
      headers: [t('tax.month'), t('tax.taxAmount'), t('tax.invoiceCount')],
      numeric: [false, true, true],
      rows: (data.taxByMonth || []).map((row: any) => [formatMonth(row.month), Number(row.taxAmount).toFixed(2), row.invoiceCount]),
      totals: [t('report.total'), Number(taxTotal.value).toFixed(2), taxInvoiceTotal.value],
    })
    sections.push({
      title: t('tax.complianceTitle'),
      headers: [t('report.metric'), t('report.value')],
      numeric: [false, true],
      rows: [
        [t('tax.totalTax'), `¥${fmt(data.totalTax)}`],
        [t('tax.invoicedAmount'), `¥${fmt(data.invoicedAmount)}`],
        [t('tax.invoices'), data.invoiceCount],
        [t('tax.effectiveRate'), `${data.effectiveTaxRate.toFixed(1)}%`],
      ],
    })
  } else if (id === 8) {
    sections.push({
      title: t('quotation.trendTitle'),
      headers: [t('quotation.month'), t('quotation.quotations'), t('quotation.orders'), t('quotation.conversion')],
      numeric: [false, true, true, true],
      rows: (data.monthlyTrend || []).map((row: any) => [formatMonth(row.month), row.quotations, row.orders, `${Number(row.conversionRate).toFixed(1)}%`]),
      totals: [t('report.total'), quotationTotal.value, convertedTotal.value, `${data.conversionRate.toFixed(1)}%`],
    })
    sections.push({
      title: t('quotation.pipelineTitle'),
      headers: [t('report.metric'), t('report.value')],
      numeric: [false, true],
      rows: [
        [t('quotation.pipelineVolume'), data.totalQuotations],
        [t('quotation.won'), data.convertedQuotations],
        [t('quotation.open'), data.openQuotations],
        [t('quotation.conversionRate'), `${data.conversionRate.toFixed(1)}%`],
      ],
    })
  }

  if (!sections.length) {
    alert(t('report.noExport'))
    return
  }

  const html = renderExcelHtml(title, sections)
  const blob = new Blob([`\ufeff${html}`], { type: 'application/vnd.ms-excel;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${title.replace(/\s+/g, '-')}.xls`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function escapeHtml(value: string | number): string {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function renderExcelHtml(title: string, sections: ExcelSection[]): string {
  const sectionHtml = sections.map((section) => {
    const colCount = section.headers.length
    const numeric = section.numeric || section.headers.map(() => false)
    const headerCells = section.headers.map((header, idx) => `<th class="${numeric[idx] ? 'num' : 'text'}">${escapeHtml(header)}</th>`).join('')
    const bodyRows = section.rows.map((row) => {
      const cells = section.headers.map((_, idx) => `<td class="${numeric[idx] ? 'num' : 'text'}">${escapeHtml(row[idx] ?? '')}</td>`).join('')
      return `<tr>${cells}</tr>`
    }).join('')
    const totalRow = section.totals
      ? `<tr class="total">${section.headers.map((_, idx) => `<td class="${numeric[idx] ? 'num' : 'text'}">${escapeHtml(section.totals?.[idx] ?? '')}</td>`).join('')}</tr>`
      : ''
    return `<table class="section-table"><tr><td class="section-title" colspan="${colCount}">${escapeHtml(section.title)}</td></tr><tr>${headerCells}</tr>${bodyRows}${totalRow}</table>`
  }).join('<div class="spacer"></div>')

  return `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="UTF-8"><style>
    body { font-family: Arial, sans-serif; font-size: 10pt; color: #111; margin: 18px; }
    .report-title { font-size: 14pt; font-weight: 700; margin-bottom: 2px; }
    .report-meta { font-size: 9pt; color: #444; margin-bottom: 2px; }
    .spacer { height: 14px; }
    .section-table { border-collapse: collapse; width: 100%; border-top: 2px solid #000; border-bottom: 2px solid #000; margin-top: 10px; }
    .section-title { font-size: 10.5pt; font-weight: 700; background: #f2f2f2; padding: 6px 7px; border-bottom: 1px solid #555; }
    th { font-size: 9pt; font-weight: 700; color: #222; border-bottom: 1px solid #000; padding: 5px 7px; white-space: normal; word-wrap: break-word; }
    td { border-bottom: 1px solid #e5e5e5; padding: 5px 7px; white-space: normal; word-wrap: break-word; vertical-align: top; mso-wrap-text: yes; }
    tr.total td { border-top: 1px solid #000; border-bottom: none; font-weight: 700; background: #fafafa; }
    .num { text-align: right; }
    .text { text-align: left; }
    td, th { mso-number-format:'\\@'; }
  </style></head><body>
    <div class="report-title">${escapeHtml(title)}</div>
    <div class="report-meta">${escapeHtml(t('report.asOf'))} ${escapeHtml(todayStr.value)}</div>
    <div class="report-meta">${escapeHtml(t('report.generatedBy'))}</div>
    <div class="report-meta">${escapeHtml(t('report.currencyNote'))}</div>
    ${sectionHtml}
  </body></html>`
}
</script>

<style scoped>
.page{padding:28px 36px;max-width:1200px;margin:0 auto;}
.header-card{display:flex;align-items:center;background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:16px;padding:20px 24px;border:1px solid rgba(173,188,159,0.18);box-shadow:0 2px 8px rgba(173,188,159,0.12);margin-bottom:20px;}
.hc-left{display:flex;align-items:center;gap:14px;}
.hc-icon{width:44px;height:44px;border-radius:12px;background:rgba(67,104,80,0.08);display:flex;align-items:center;justify-content:center;}
.hc-title{font-size:18px;font-weight:800;color:#12372A;margin:0;}
.hc-sub{font-size:12px;color:rgba(18,55,42,0.45);margin:2px 0 0;}

.report-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px;}
.report-card{display:flex;gap:16px;background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:14px;padding:20px;border:1px solid rgba(173,188,159,0.15);box-shadow:0 2px 8px rgba(173,188,159,0.1);transition:all 0.25s;}
.report-card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(173,188,159,0.18);border-color:rgba(67,104,80,0.15);}
.rc-icon{width:48px;height:48px;border-radius:12px;background:rgba(67,104,80,0.06);display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.rc-body{flex:1;min-width:0;display:flex;flex-direction:column;}
.rc-title{font-size:15px;font-weight:700;color:#12372A;margin:0 0 6px;}
.rc-desc{font-size:12px;color:rgba(18,55,42,0.45);line-height:1.5;margin:0 0 10px;}
.rc-meta{display:flex;align-items:center;gap:10px;margin-bottom:12px;}
.rc-tag{font-size:10px;font-weight:600;background:rgba(67,104,80,0.08);color:#436850;padding:3px 10px;border-radius:4px;text-transform:uppercase;letter-spacing:0.4px;}
.rc-date{font-size:11px;color:rgba(18,55,42,0.3);}
.rc-btn{align-self:flex-start;padding:8px 18px;font-size:12px;}

.result-container{background:linear-gradient(145deg,#fdfce8,#f7f5d1);border-radius:16px;padding:24px;border:1px solid rgba(173,188,159,0.18);}
.result-header{margin-bottom:16px;}
.back-link{background:none;border:none;color:#436850;cursor:pointer;display:flex;align-items:center;gap:4px;font-weight:600;font-size:13px;margin-bottom:12px;}
.rh-main{display:flex;justify-content:space-between;align-items:center;}
.rh-main h3{font-size:20px;font-weight:800;color:#12372A;margin:0;}
.rh-actions{display:flex;gap:10px;}
.period-select{height:32px;padding:0 30px 0 10px;border:1px solid rgba(173,188,159,0.45);border-radius:8px;background:#fff;color:#436850;font-size:12px;font-family:inherit;outline:none;cursor:pointer;}

/* Mode selector */
.mode-selector{display:flex;gap:8px;margin-bottom:20px;background:rgba(173,188,159,0.12);padding:5px;border-radius:10px;width:fit-content;}
.mode-btn{display:flex;align-items:center;gap:6px;padding:8px 18px;font-size:13px;font-weight:600;border:none;border-radius:8px;cursor:pointer;transition:all 0.2s;background:transparent;color:rgba(18,55,42,0.5);font-family:inherit;}
.mode-btn.active{background:#fff;color:#436850;box-shadow:0 2px 6px rgba(67,104,80,0.08);}
.mode-btn:hover:not(.active){color:rgba(18,55,42,0.7);}

.loading-state{padding:60px;text-align:center;color:rgba(18,55,42,0.4);}
.spinner{width:32px;height:32px;border:3px solid rgba(67,104,80,0.1);border-top-color:#436850;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 16px;}
@keyframes spin{to{transform:rotate(360deg);}}

/* Sales KPI */
.kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px;}
.kpi-card{background:rgba(255,255,255,0.4);border-radius:12px;padding:16px;border:1px solid rgba(173,188,159,0.2);}
.kpi-card label{font-size:11px;font-weight:700;color:rgba(18,55,42,0.4);text-transform:uppercase;display:block;margin-bottom:4px;}
.kpi-card .value{font-size:20px;font-weight:800;color:#12372A;}
.kpi-sub{font-size:11px;color:rgba(18,55,42,0.3);margin-top:2px;display:block;}
.kpi-row-4{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px;}
.kpi-row-2{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-bottom:22px;max-width:640px;}
.kpi-row-4 .kpi-card,.kpi-row-2 .kpi-card{background:#fff;border-radius:12px;padding:16px;border:1px solid rgba(173,188,159,0.15);box-shadow:0 2px 8px rgba(0,0,0,0.02);}
.kpi-row-4 .kpi-card .value,.kpi-row-2 .kpi-card .value{font-size:22px;font-weight:800;color:#12372A;}

/* Overview Mode — 6 KPI cards */
.kpi-row-6{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px;}
.kpi-card.primary{border-left:4px solid #436850;}
.kpi-card.danger{border-left:4px solid #D9534F;}
.kpi-card.success{border-left:4px solid #5CB85C;}
.kpi-card.info{border-left:4px solid #5BC0DE;}
.kpi-card.warn{border-left:4px solid #F0AD4E;}
.kpi-row-6 .kpi-card{background:#fff;border-radius:12px;padding:16px;border:1px solid rgba(173,188,159,0.15);box-shadow:0 2px 8px rgba(0,0,0,0.02);}
.kpi-row-6 .kpi-card .value{font-size:22px;font-weight:800;color:#12372A;}

/* Overview grid */
.overview-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
.panel{background:#fff;border-radius:14px;padding:20px;border:1px solid rgba(173,188,159,0.15);box-shadow:0 2px 8px rgba(0,0,0,0.02);}
.panel-title{display:flex;align-items:center;gap:8px;font-size:14px;font-weight:700;color:#12372A;margin:0 0 16px;}
.panel-title svg{color:rgba(67,104,80,0.5);}
.insight-list{display:flex;flex-direction:column;gap:12px;}
.insight-item{display:flex;align-items:center;gap:10px;font-size:13px;color:rgba(18,55,42,0.72);}
.insight-item b{color:#12372A;}
.insight-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0;}
.insight-dot.primary{background:#436850;}
.insight-dot.success{background:#5CB85C;}
.insight-dot.info{background:#5BC0DE;}
.insight-dot.warning{background:#F0AD4E;}
.mini-badge{display:inline-block;margin-left:6px;padding:2px 7px;border-radius:999px;background:rgba(92,184,92,0.14);color:#3e9a4d;font-size:10px;font-weight:700;}
.highlight-row{background:rgba(92,184,92,0.06);}
.report-table tfoot td{border-top:2px solid rgba(173,188,159,0.28);background:rgba(173,188,159,0.05);font-weight:600;}
.delivery-status{background:linear-gradient(90deg,#436850,#5a8a68);}
.inventory-category{background:linear-gradient(90deg,#5BC0DE,#436850);}

/* Status distribution bars */
.status-bars{display:flex;flex-direction:column;gap:14px;}
.status-bar-item{}
.sb-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;}
.sb-label{font-size:13px;font-weight:600;color:#12372A;}
.sb-amount{font-size:13px;font-weight:600;color:#12372A;font-family:'SF Mono',Consolas,monospace;}
.sb-track{height:8px;background:rgba(173,188,159,0.15);border-radius:4px;overflow:hidden;}
.sb-fill{height:100%;border-radius:4px;transition:width 0.4s;}
.sb-fill.st-cleared{background:#5CB85C;}
.sb-fill.st-partial{background:#F0AD4E;}
.sb-fill.st-open{background:#5BC0DE;}
.sb-fill.st-void{background:#D9534F;}
.sb-meta{font-size:11px;color:rgba(18,55,42,0.35);margin-top:3px;display:block;}

/* AR Aging */
.aging-list{display:flex;flex-direction:column;gap:14px;}
.aging-item{}
.aging-info{display:flex;justify-content:space-between;margin-bottom:5px;}
.aging-bucket{font-size:13px;font-weight:600;color:#12372A;}
.aging-amount{font-size:13px;font-weight:600;color:#12372A;font-family:'SF Mono',Consolas,monospace;}
.aging-bar-track{height:8px;background:rgba(173,188,159,0.15);border-radius:4px;overflow:hidden;}
.aging-bar-fill{height:100%;border-radius:4px;}
.aging-bar-fill.success{background:#5CB85C;}
.aging-bar-fill.warning{background:#F0AD4E;}
.aging-bar-fill.danger{background:#D9534F;}

/* Top customers */
.top-customer-list{display:flex;flex-direction:column;gap:10px;}
.tc-item{display:flex;align-items:center;gap:12px;padding:10px;border-radius:10px;background:rgba(173,188,159,0.06);}
.tc-rank{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800;flex-shrink:0;}
.tc-rank.rank-1{background:#436850;color:#FBFADA;}
.tc-rank.rank-2{background:rgba(67,104,80,0.7);color:#FBFADA;}
.tc-rank.rank-3{background:rgba(67,104,80,0.5);color:#FBFADA;}
.tc-rank.rank-4,.tc-rank.rank-5{background:rgba(173,188,159,0.3);color:#436850;}
.tc-info{flex:1;display:flex;flex-direction:column;gap:1px;min-width:0;}
.tc-name{font-size:13px;font-weight:600;color:#12372A;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.tc-id{font-size:11px;color:rgba(18,55,42,0.3);font-family:'SF Mono',Consolas,monospace;}
.tc-amount{font-size:14px;font-weight:700;font-family:'SF Mono',Consolas,monospace;flex-shrink:0;}
.danger-text{color:#D9534F;}

/* Collection trend */
.trend-chart{padding:10px 0;}
.trend-bars{display:flex;align-items:flex-end;gap:14px;height:180px;}
.trend-col{flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;}
.trend-bar{width:100%;max-width:50px;background:linear-gradient(180deg,#436850,#5a8a68);border-radius:6px 6px 0 0;display:flex;align-items:flex-start;justify-content:center;min-height:4px;transition:height 0.4s;}
.trend-val{font-size:10px;color:#FBFADA;font-weight:600;padding-top:6px;white-space:nowrap;}
.trend-month{font-size:11px;color:rgba(18,55,42,0.4);font-weight:600;}

.empty-mini{padding:20px;text-align:center;font-size:13px;color:rgba(18,55,42,0.3);}

/* Table basics */
.table-wrap{overflow-x:auto;}
.report-table{width:100%;border-collapse:collapse;}
.report-table th{text-align:left;padding:12px;font-size:11px;font-weight:700;color:rgba(18,55,42,0.4);text-transform:uppercase;border-bottom:2px solid rgba(173,188,159,0.2);}
.report-table td{padding:12px;border-bottom:1px solid rgba(173,188,159,0.1);font-size:14px;}
.num{text-align:right;}
.mono{font-family:'SF Mono',monospace;}
.mono-sm{font-family:'SF Mono',Consolas,monospace;font-size:12px;}
.bold{font-weight:700;}

/* Delivery / Finance cards */
.fin-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;}
.fin-card{background:#fff;padding:24px;border-radius:16px;border-left:6px solid #436850;box-shadow:0 4px 12px rgba(0,0,0,0.03);}
.fin-card.warn{border-left-color:#F0AD4E;}
.fin-card.success{border-left-color:#5CB85C;}
.fin-card.info{border-left-color:#5BC0DE;}
.fc-header{margin-bottom:8px;}
.fc-header .label{font-size:12px;font-weight:700;color:rgba(0,0,0,0.4);text-transform:uppercase;}
.fc-val{font-size:28px;font-weight:800;color:#12372A;}

.empty-result{padding:60px;text-align:center;color:rgba(18,55,42,0.3);display:flex;flex-direction:column;align-items:center;gap:16px;}

/* ========== Statement Mode ========== */
.statement-view{max-width:960px;margin:0 auto;}
.stmt-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:28px;padding-bottom:16px;border-bottom:2px solid #12372A;}
.stmt-title{font-size:22px;font-weight:800;color:#12372A;margin:0;}
.stmt-period{font-size:13px;color:rgba(18,55,42,0.5);margin:4px 0 0;}
.stmt-stamp{font-size:11px;font-weight:700;color:rgba(67,104,80,0.4);text-transform:uppercase;letter-spacing:1px;border:1.5px solid rgba(67,104,80,0.2);padding:6px 12px;border-radius:6px;}

.stmt-section{margin-bottom:32px;}
.stmt-section-title{font-size:14px;font-weight:700;color:#436850;margin:0 0 12px;padding-bottom:6px;border-bottom:1px solid rgba(173,188,159,0.25);}

.stmt-table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;}
.stmt-table th{padding:10px 14px;font-size:11px;font-weight:700;color:rgba(18,55,42,0.5);text-transform:uppercase;border-bottom:2px solid rgba(173,188,159,0.25);background:rgba(173,188,159,0.06);}
.stmt-table th.left{text-align:left;}
.stmt-table th.num{text-align:right;}
.stmt-table th.center{text-align:center;}
.stmt-table td{padding:10px 14px;border-bottom:1px solid rgba(173,188,159,0.08);font-size:13px;color:#12372A;}
.stmt-table td.left{text-align:left;}
.stmt-table td.num{text-align:right;}
.stmt-table td.center{text-align:center;}
.stmt-table td.muted{color:rgba(18,55,42,0.3);}
.stmt-table tfoot td{border-top:2px solid rgba(173,188,159,0.25);border-bottom:none;background:rgba(173,188,159,0.05);}
.stmt-table tfoot td.bold{font-weight:700;}
.stmt-table tbody tr:hover{background:rgba(173,188,159,0.04);}

.status-tag{display:inline-block;font-size:11px;font-weight:600;padding:2px 10px;border-radius:4px;text-transform:uppercase;}
.status-tag.st-cleared{background:rgba(92,184,92,0.12);color:#5CB85C;}
.status-tag.st-partial{background:rgba(240,173,78,0.12);color:#F0AD4E;}
.status-tag.st-open{background:rgba(91,192,222,0.12);color:#5BC0DE;}
.status-tag.st-void{background:rgba(217,83,79,0.12);color:#D9534F;}

.risk-tag{display:inline-block;font-size:11px;font-weight:600;padding:2px 10px;border-radius:4px;text-transform:uppercase;}
.risk-tag.rk-high{background:rgba(217,83,79,0.12);color:#D9534F;}
.risk-tag.rk-medium{background:rgba(240,173,78,0.12);color:#F0AD4E;}
.risk-tag.rk-low{background:rgba(92,184,92,0.12);color:#5CB85C;}

.risk-row{}

.stmt-footer{margin-top:28px;padding-top:16px;border-top:1px solid rgba(173,188,159,0.2);text-align:center;}
.stmt-footer p{font-size:11px;color:rgba(18,55,42,0.3);margin:2px 0;}

/* Buttons */
.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 20px;font-size:13px;font-weight:600;border-radius:8px;cursor:pointer;transition:all 0.2s;font-family:inherit;border:none;}
.btn-sm{padding:6px 14px;font-size:12px;}
.btn-primary{background:linear-gradient(135deg,#436850,#365440);color:#FBFADA;}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(67,104,80,0.25);}
.btn-outline{background:transparent;border:1.5px solid rgba(67,104,80,0.3);color:#436850;}
.btn-outline:hover{background:rgba(67,104,80,0.05);}
</style>
