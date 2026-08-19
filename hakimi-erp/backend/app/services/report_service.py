from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from app.models.sales import SalesOrder, SalesOrderItem, Quotation
from app.models.finance import Invoice, InvoiceItem, OpenAccountReceivable, ClosedAccountReceivable, Receipt
from app.models.logistics import Delivery
from app.models.customer import BusinessPartner
from app.models.material import Material, PricingCondition
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from decimal import Decimal

class ReportService:
    @staticmethod
    def get_sales_performance(db: Session, days: int = 30) -> Dict[str, Any]:
        start_date = datetime.now() - timedelta(days=days)
        
        # Aggregate sales by date
        sales_by_date = db.query(
            func.date(SalesOrder.created_time).label('date'),
            func.sum(SalesOrder.net_value).label('total_value'),
            func.count(SalesOrder.sales_order_id).label('order_count')
        ).filter(SalesOrder.created_time >= start_date)\
         .group_by(func.date(SalesOrder.created_time))\
         .order_by(func.date(SalesOrder.created_time)).all()
        
        return {
            "labels": [str(s.date) for s in sales_by_date],
            "values": [float(s.total_value or 0) for s in sales_by_date],
            "counts": [s.order_count for s in sales_by_date]
        }

    @staticmethod
    def get_financial_summary(db: Session) -> Dict[str, Any]:
        total_invoiced = db.query(func.sum(Invoice.total_amount)).filter(Invoice.status != 'VOID').scalar() or 0
        open_ar = db.query(func.sum(OpenAccountReceivable.receivable_amount - OpenAccountReceivable.received_amount)).scalar() or 0
        collected = db.query(func.sum(ClosedAccountReceivable.received_amount)).scalar() or 0
        
        return {
            "total_invoiced": float(total_invoiced),
            "open_receivables": float(open_ar),
            "collected_amount": float(collected),
            "collection_rate": float(collected / total_invoiced * 100) if total_invoiced > 0 else 0
        }

    @staticmethod
    def get_delivery_stats(db: Session) -> Dict[str, Any]:
        total_deliveries = db.query(func.count(Delivery.delivery_id)).scalar() or 0
        completed = db.query(func.count(Delivery.delivery_id)).filter(Delivery.delivery_status == 'PGI_DONE').scalar() or 0
        pending = total_deliveries - completed

        status_rows = db.query(
            Delivery.delivery_status,
            func.count(Delivery.delivery_id)
        ).group_by(Delivery.delivery_status).all()

        monthly_rows = db.query(
            func.date_format(Delivery.created_time, '%Y-%m').label('month'),
            func.count(Delivery.delivery_id)
        ).group_by('month').order_by('month').all()

        on_time = 0
        try:
            on_time = db.query(func.count(Delivery.delivery_id)).filter(
                Delivery.delivery_status == 'PGI_DONE',
                func.date(Delivery.actual_gi_date) <= Delivery.planned_gi_date
            ).scalar() or 0
        except Exception:
            on_time = 0

        status_labels = {
            "OPEN": "Open",
            "PICKING": "Picking",
            "SHIPPED": "Shipped",
            "IN_TRANSIT": "In Transit",
            "PGI_DONE": "Completed",
            "CANCELLED": "Cancelled",
        }
        
        return {
            "total": total_deliveries,
            "completed": completed,
            "pending": pending,
            "completion_rate": float(completed / total_deliveries * 100) if total_deliveries > 0 else 0,
            "on_time": on_time,
            "on_time_rate": float(on_time / completed * 100) if completed > 0 else 0,
            "status_breakdown": [
                {
                    "status": status,
                    "label": status_labels.get(status, status),
                    "count": int(count or 0),
                    "percentage": float(count / total_deliveries * 100) if total_deliveries > 0 else 0,
                }
                for status, count in sorted(status_rows, key=lambda x: -(x[1] or 0))
            ],
            "monthly_trend": [
                {"month": str(month), "count": int(count or 0)}
                for month, count in monthly_rows
            ],
        }

    @staticmethod
    def get_customer_analysis(db: Session) -> Dict[str, Any]:
        total_customers = db.query(func.count(BusinessPartner.bp_id)).scalar() or 0
        active_customers = db.query(func.count(BusinessPartner.bp_id)).filter(BusinessPartner.status == 'ACTIVE').scalar() or 0

        order_rows = db.query(
            SalesOrder.customer_id,
            func.sum(SalesOrder.net_value),
            func.count(SalesOrder.sales_order_id),
        ).filter(SalesOrder.status != 'CANCELLED').group_by(SalesOrder.customer_id).all()

        bp_names = dict(db.query(BusinessPartner.bp_id, BusinessPartner.bp_name).all())
        top_customers = sorted(
            [
                {
                    "bp_id": bp or "",
                    "bp_name": bp_names.get(bp, bp or ""),
                    "order_count": int(order_count or 0),
                    "revenue": float(revenue or 0),
                }
                for bp, revenue, order_count in order_rows
            ],
            key=lambda x: x["revenue"],
            reverse=True,
        )[:10]

        six_months_ago = datetime.now() - timedelta(days=180)
        new_customer_rows = db.query(
            func.date_format(BusinessPartner.created_time, '%Y-%m').label('month'),
            func.count(BusinessPartner.bp_id),
        ).filter(BusinessPartner.created_time >= six_months_ago).group_by('month').all()

        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "blocked_customers": total_customers - active_customers,
            "top_customers": top_customers,
            "new_customers_trend": [
                {"month": str(month), "count": int(count)}
                for month, count in sorted(new_customer_rows, key=lambda x: x[0])
            ],
        }

    @staticmethod
    def get_inventory_turnover(db: Session) -> Dict[str, Any]:
        materials = db.query(Material).all()
        sold_rows = db.query(
            SalesOrderItem.material_id,
            func.sum(SalesOrderItem.order_quantity),
        ).group_by(SalesOrderItem.material_id).all()
        sold_by_material = {material_id: float(qty or 0) for material_id, qty in sold_rows}

        category_stock: Dict[str, float] = {}
        total_stock = 0.0
        low_stock_count = 0
        turnover = []

        for material in materials:
            stock = float(material.stock_quantity or 0)
            sold_quantity = sold_by_material.get(material.material_id, 0)
            total_stock += stock
            if stock < 10:
                low_stock_count += 1

            category = material.category or "Uncategorized"
            category_stock[category] = category_stock.get(category, 0) + stock

            turnover.append({
                "material_id": material.material_id,
                "material_name": material.material_name,
                "category": category,
                "stock": stock,
                "sold_quantity": sold_quantity,
                "turnover_rate": round(sold_quantity / stock, 4) if stock > 0 else 0,
            })

        turnover.sort(key=lambda x: x["turnover_rate"], reverse=True)
        return {
            "material_count": len(materials),
            "total_stock": total_stock,
            "low_stock_count": low_stock_count,
            "inventory_turnover": turnover[:20],
            "category_summary": [
                {"category": key, "stock": value}
                for key, value in sorted(category_stock.items(), key=lambda x: x[1], reverse=True)
            ],
        }

    @staticmethod
    def get_pricing_conditions_report(db: Session) -> Dict[str, Any]:
        conditions = db.query(PricingCondition).all()
        by_type: Dict[str, Dict[str, float]] = {}

        for condition in conditions:
            condition_type = condition.condition_type or "OTHER"
            entry = by_type.setdefault(condition_type, {"count": 0, "rate_sum": 0.0, "amount_sum": 0.0})
            entry["count"] += 1
            entry["rate_sum"] += float(condition.rate or 0)
            entry["amount_sum"] += float(condition.amount or 0)

        by_type_rows = [
            {
                "condition_type": condition_type,
                "count": int(entry["count"]),
                "average_rate": round(entry["rate_sum"] / entry["count"], 2),
                "average_amount": round(entry["amount_sum"] / entry["count"], 2),
            }
            for condition_type, entry in sorted(by_type.items())
        ]

        top_conditions = sorted(
            [
                {
                    "condition_id": condition.condition_id,
                    "condition_type": condition.condition_type,
                    "condition_name": condition.condition_name,
                    "rate": float(condition.rate or 0),
                    "amount": float(condition.amount or 0),
                    "status": condition.status,
                }
                for condition in conditions
            ],
            key=lambda x: x["amount"],
            reverse=True,
        )[:10]

        return {
            "total_conditions": len(conditions),
            "active_conditions": sum(1 for c in conditions if c.status == 'ACTIVE'),
            "type_count": len(by_type_rows),
            "by_type": by_type_rows,
            "top_conditions": top_conditions,
        }

    @staticmethod
    def get_tax_compliance_report(db: Session) -> Dict[str, Any]:
        invoices = db.query(Invoice).filter(Invoice.status != 'VOID').all()
        invoiced_amount = float(sum((invoice.total_amount or 0) for invoice in invoices))
        invoice_count = len(invoices)

        item_rows = db.query(InvoiceItem.tax_amount, Invoice.invoice_date).join(
            Invoice, InvoiceItem.invoice_id == Invoice.invoice_id
        ).filter(Invoice.status != 'VOID').all()

        tax_by_month: Dict[str, float] = {}
        invoice_by_month: Dict[str, int] = {}
        for invoice in invoices:
            month = invoice.invoice_date.strftime('%Y-%m') if invoice.invoice_date else 'Unknown'
            invoice_by_month[month] = invoice_by_month.get(month, 0) + 1

        for tax_amount, invoice_date in item_rows:
            month = invoice_date.strftime('%Y-%m') if invoice_date else 'Unknown'
            tax_by_month[month] = tax_by_month.get(month, 0) + float(tax_amount or 0)

        all_months = sorted(set(tax_by_month) | set(invoice_by_month))
        return {
            "total_tax": float(sum(tax_by_month.values())),
            "invoiced_amount": invoiced_amount,
            "invoice_count": invoice_count,
            "effective_tax_rate": round((sum(tax_by_month.values()) / invoiced_amount * 100), 2) if invoiced_amount > 0 else 0,
            "tax_by_month": [
                {"month": month, "tax_amount": tax_by_month.get(month, 0), "invoice_count": invoice_by_month.get(month, 0)}
                for month in all_months[-12:]
            ],
        }

    @staticmethod
    def get_quotation_conversion_report(db: Session) -> Dict[str, Any]:
        quotations = db.query(Quotation).all()
        orders = db.query(SalesOrder).filter(SalesOrder.quotation_id.isnot(None)).all()
        converted_ids = {order.quotation_id for order in orders}

        total_quotations = len(quotations)
        converted_quotations = sum(1 for q in quotations if q.quotation_id in converted_ids)
        open_quotations = sum(1 for q in quotations if q.status == 'OPEN')
        cancelled_quotations = sum(1 for q in quotations if q.status in ('CANCELLED', 'CLOSED'))

        quotation_by_month: Dict[str, int] = {}
        order_by_month: Dict[str, int] = {}
        for quotation in quotations:
            if quotation.created_time:
                month = quotation.created_time.strftime('%Y-%m')
                quotation_by_month[month] = quotation_by_month.get(month, 0) + 1
        for order in orders:
            if order.created_time:
                month = order.created_time.strftime('%Y-%m')
                order_by_month[month] = order_by_month.get(month, 0) + 1

        all_months = sorted(set(quotation_by_month) | set(order_by_month))
        monthly_trend = []
        for month in all_months[-12:]:
            quotations_count = quotation_by_month.get(month, 0)
            orders_count = order_by_month.get(month, 0)
            monthly_trend.append({
                "month": month,
                "quotations": quotations_count,
                "orders": orders_count,
                "conversion_rate": round(orders_count / quotations_count * 100, 2) if quotations_count > 0 else 0,
            })

        return {
            "total_quotations": total_quotations,
            "converted_quotations": converted_quotations,
            "open_quotations": open_quotations,
            "cancelled_quotations": cancelled_quotations,
            "conversion_rate": round(converted_quotations / total_quotations * 100, 2) if total_quotations > 0 else 0,
            "monthly_trend": monthly_trend,
        }

    # ================================================================
    #  Financial Detail Report — two modes: overview + statement
    # ================================================================
    @staticmethod
    def get_financial_detail(db: Session) -> Dict[str, Any]:
        today = date.today()

        # ---- 1. KPI summary ----
        total_invoiced = db.query(func.sum(Invoice.total_amount)).filter(Invoice.status != 'VOID').scalar() or Decimal(0)
        void_amount = db.query(func.sum(Invoice.total_amount)).filter(Invoice.status == 'VOID').scalar() or Decimal(0)

        # Open AR
        open_ar_rows = db.query(
            OpenAccountReceivable, Invoice
        ).join(Invoice, OpenAccountReceivable.invoice_id == Invoice.invoice_id).all()

        open_receivable_total = Decimal(0)
        received_so_far = Decimal(0)
        overdue_amount = Decimal(0)
        aging_buckets = {"current": Decimal(0), "1_30": Decimal(0), "31_60": Decimal(0), "61_90": Decimal(0), "90_plus": Decimal(0)}

        for ar, inv in open_ar_rows:
            outstanding = ar.receivable_amount - ar.received_amount
            open_receivable_total += outstanding
            received_so_far += ar.received_amount
            if ar.due_date and ar.due_date < today:
                overdue_amount += outstanding
                days_overdue = (today - ar.due_date).days
                if days_overdue <= 30:
                    aging_buckets["1_30"] += outstanding
                elif days_overdue <= 60:
                    aging_buckets["31_60"] += outstanding
                elif days_overdue <= 90:
                    aging_buckets["61_90"] += outstanding
                else:
                    aging_buckets["90_plus"] += outstanding
            else:
                aging_buckets["current"] += outstanding

        # Closed AR
        closed_rows = db.query(ClosedAccountReceivable).all()
        collected_amount = Decimal(0)
        for cr in closed_rows:
            collected_amount += cr.received_amount

        total_collected = received_so_far + collected_amount
        collection_rate = float(total_collected / total_invoiced * 100) if total_invoiced > 0 else 0.0

        # ---- 2. Invoice status distribution ----
        status_counts = db.query(
            Invoice.status,
            func.count(Invoice.invoice_id),
            func.sum(Invoice.total_amount)
        ).group_by(Invoice.status).all()

        status_distribution = []
        status_labels = {"OPEN": "Open", "PARTIAL": "Partial", "CLEARED": "Cleared", "VOID": "Void"}
        for s, cnt, amt in status_counts:
            status_distribution.append({
                "status": s,
                "label": status_labels.get(s, s),
                "count": cnt,
                "amount": float(amt or 0),
                "percentage": float(amt / total_invoiced * 100) if total_invoiced > 0 else 0
            })

        # ---- 3. Top 5 outstanding customers ----
        customer_outstanding = {}
        bp_names = {}
        for ar, inv in open_ar_rows:
            bp_id = inv.payer or ""
            outstanding = ar.receivable_amount - ar.received_amount
            if bp_id not in customer_outstanding:
                customer_outstanding[bp_id] = Decimal(0)
            customer_outstanding[bp_id] += outstanding

        bp_ids = list(customer_outstanding.keys())
        if bp_ids:
            bp_rows = db.query(BusinessPartner.bp_id, BusinessPartner.bp_name).filter(BusinessPartner.bp_id.in_(bp_ids)).all()
            for bp_id, bp_name in bp_rows:
                bp_names[bp_id] = bp_name

        top_customers = sorted(
            [{"bp_id": k, "bp_name": bp_names.get(k, k), "outstanding": float(v)} for k, v in customer_outstanding.items()],
            key=lambda x: x["outstanding"],
            reverse=True
        )[:5]

        # ---- 4. Monthly collection trend (last 6 months) ----
        six_months_ago = today - timedelta(days=180)
        receipts = db.query(Receipt).filter(Receipt.receipt_date >= six_months_ago).all()
        monthly_collections = {}
        for r in receipts:
            month_key = r.receipt_date.strftime("%Y-%m") if r.receipt_date else "Unknown"
            monthly_collections[month_key] = monthly_collections.get(month_key, Decimal(0)) + r.receipt_amount

        collection_trend = [
            {"month": k, "amount": float(v)}
            for k, v in sorted(monthly_collections.items())
        ]

        # ---- 5. AR aging summary ----
        aging_summary = [
            {"bucket": "Current (Not Due)", "amount": float(aging_buckets["current"]), "color": "success"},
            {"bucket": "1-30 Days", "amount": float(aging_buckets["1_30"]), "color": "warning"},
            {"bucket": "31-60 Days", "amount": float(aging_buckets["31_60"]), "color": "warning"},
            {"bucket": "61-90 Days", "amount": float(aging_buckets["61_90"]), "color": "danger"},
            {"bucket": "90+ Days", "amount": float(aging_buckets["90_plus"]), "color": "danger"},
        ]

        # ---- 6. Avg days to collect (from closed AR) ----
        avg_days_to_collect = 0.0
        if closed_rows:
            total_days = 0
            count = 0
            for cr in closed_rows:
                inv = db.query(Invoice).filter(Invoice.invoice_id == cr.invoice_id).first()
                if inv and inv.invoice_date and cr.closed_time:
                    total_days += (cr.closed_time.date() - inv.invoice_date).days
                    count += 1
            if count > 0:
                avg_days_to_collect = total_days / count

        # ================================================================
        # Statement-mode data (professional accounting tables)
        # ================================================================

        # ---- 7. AR by customer summary (beginning / invoiced / collected / ending) ----
        # "Beginning balance" = total invoiced before this month
        month_start = today.replace(day=1)

        all_invoices = db.query(Invoice).filter(Invoice.status != 'VOID').all()
        all_receipts = db.query(Receipt).all()

        customer_ar_summary = {}
        for inv in all_invoices:
            bp_id = inv.payer or ""
            if bp_id not in customer_ar_summary:
                customer_ar_summary[bp_id] = {
                    "bp_id": bp_id,
                    "bp_name": bp_names.get(bp_id, bp_id),
                    "beginning_balance": Decimal(0),
                    "invoiced_this_period": Decimal(0),
                    "collected_this_period": Decimal(0),
                    "ending_balance": Decimal(0),
                }
            if inv.invoice_date and inv.invoice_date >= month_start:
                customer_ar_summary[bp_id]["invoiced_this_period"] += inv.total_amount or Decimal(0)
            else:
                customer_ar_summary[bp_id]["beginning_balance"] += inv.total_amount or Decimal(0)
            customer_ar_summary[bp_id]["ending_balance"] += inv.total_amount or Decimal(0)

        for r in all_receipts:
            inv = next((i for i in all_invoices if i.invoice_id == r.invoice_id), None)
            bp_id = inv.payer if inv else r.payer or ""
            if bp_id not in customer_ar_summary:
                customer_ar_summary[bp_id] = {
                    "bp_id": bp_id,
                    "bp_name": bp_names.get(bp_id, bp_id),
                    "beginning_balance": Decimal(0),
                    "invoiced_this_period": Decimal(0),
                    "collected_this_period": Decimal(0),
                    "ending_balance": Decimal(0),
                }
            customer_ar_summary[bp_id]["collected_this_period"] += r.receipt_amount or Decimal(0)
            customer_ar_summary[bp_id]["ending_balance"] -= r.receipt_amount or Decimal(0)

        # Fill in bp names
        all_bp_ids = list(customer_ar_summary.keys())
        if all_bp_ids:
            bp_rows = db.query(BusinessPartner.bp_id, BusinessPartner.bp_name).filter(BusinessPartner.bp_id.in_(all_bp_ids)).all()
            for bp_id, bp_name in bp_rows:
                if bp_id in customer_ar_summary:
                    customer_ar_summary[bp_id]["bp_name"] = bp_name

        ar_by_customer = sorted(
            [{
                **v,
                "beginning_balance": float(v["beginning_balance"]),
                "invoiced_this_period": float(v["invoiced_this_period"]),
                "collected_this_period": float(v["collected_this_period"]),
                "ending_balance": float(v["ending_balance"]),
            } for v in customer_ar_summary.values()],
            key=lambda x: x["ending_balance"],
            reverse=True
        )

        # ---- 8. Receipt ledger (all receipts) ----
        receipt_ledger = []
        for r in all_receipts:
            inv = next((i for i in all_invoices if i.invoice_id == r.invoice_id), None)
            bp_id = inv.payer if inv else r.payer or ""
            bp_name = bp_names.get(bp_id, bp_id)
            receipt_ledger.append({
                "receipt_id": r.receipt_id,
                "invoice_id": r.invoice_id,
                "bp_id": bp_id,
                "bp_name": bp_name,
                "amount": float(r.receipt_amount or 0),
                "receipt_date": r.receipt_date.strftime("%Y-%m-%d") if r.receipt_date else "",
                "payment_method": r.payment_method or "",
                "reference_no": r.reference_no or "",
            })
        receipt_ledger.sort(key=lambda x: x["receipt_date"], reverse=True)

        # ---- 9. Invoice summary by status ----
        invoice_summary = []
        for s, cnt, amt in status_counts:
            invoice_summary.append({
                "status": s,
                "label": status_labels.get(s, s),
                "count": cnt,
                "amount": float(amt or 0),
                "percentage": float(amt / total_invoiced * 100) if total_invoiced > 0 else 0
            })

        # ---- 10. Overdue analysis (per invoice) ----
        overdue_invoices = []
        for ar, inv in open_ar_rows:
            if ar.due_date and ar.due_date < today:
                outstanding = ar.receivable_amount - ar.received_amount
                dp_id = inv.payer or ""
                days_overdue = (today - ar.due_date).days
                if days_overdue > 90:
                    risk_level = "High"
                elif days_overdue > 60:
                    risk_level = "Medium"
                else:
                    risk_level = "Low"
                overdue_invoices.append({
                    "invoice_id": inv.invoice_id,
                    "bp_id": dp_id,
                    "bp_name": bp_names.get(dp_id, dp_id),
                    "invoice_date": inv.invoice_date.strftime("%Y-%m-%d") if inv.invoice_date else "",
                    "due_date": ar.due_date.strftime("%Y-%m-%d"),
                    "days_overdue": days_overdue,
                    "outstanding": float(outstanding),
                    "risk_level": risk_level,
                })
        overdue_invoices.sort(key=lambda x: x["days_overdue"], reverse=True)

        return {
            # KPI cards
            "total_invoiced": float(total_invoiced),
            "void_amount": float(void_amount),
            "open_receivables": float(open_receivable_total),
            "collected_amount": float(total_collected),
            "overdue_amount": float(overdue_amount),
            "collection_rate": collection_rate,
            "avg_days_to_collect": avg_days_to_collect,
            "invoice_count": len(all_invoices),

            # Overview mode
            "status_distribution": status_distribution,
            "aging_summary": aging_summary,
            "top_customers": top_customers,
            "collection_trend": collection_trend,

            # Statement mode
            "ar_by_customer": ar_by_customer,
            "receipt_ledger": receipt_ledger,
            "invoice_summary": invoice_summary,
            "overdue_invoices": overdue_invoices,
        }

    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict[str, Any]:
        """Return reliable dashboard KPIs with period-over-period comparisons."""
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        yesterday_start = today_start - timedelta(days=1)

        month_start = datetime(now.year, now.month, 1)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        def calc_change(current, previous):
            if not previous or previous == 0:
                return "+100%" if current > 0 else "0%"
            change = ((current - previous) / previous) * 100
            return f"{'+' if change >= 0 else ''}{change:.1f}%"

        def count_orders_since(start: datetime, end: datetime | None = None) -> int:
            query = db.query(func.count(SalesOrder.sales_order_id)).filter(
                SalesOrder.created_time >= start,
                SalesOrder.status != 'CANCELLED',
            )
            if end is not None:
                query = query.filter(SalesOrder.created_time < end)
            return int(query.scalar() or 0)

        def count_deliveries_since(start: datetime, end: datetime | None = None) -> int:
            try:
                query = db.query(func.count(Delivery.delivery_id)).filter(Delivery.created_time >= start)
                if end is not None:
                    query = query.filter(Delivery.created_time < end)
                return int(query.scalar() or 0)
            except Exception:
                return 0

        def gross_profit_since(start: datetime, end: datetime | None = None) -> float:
            try:
                query = db.query(
                    func.sum(
                        (SalesOrderItem.net_price - Material.standard_price)
                        * SalesOrderItem.order_quantity
                    )
                ).join(
                    Material, SalesOrderItem.material_id == Material.material_id
                ).join(
                    SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.sales_order_id
                ).filter(
                    SalesOrder.created_time >= start,
                    SalesOrder.status != 'CANCELLED',
                )
                if end is not None:
                    query = query.filter(SalesOrder.created_time < end)
                return float(query.scalar() or 0)
            except Exception:
                return 0.0

        today_orders = count_orders_since(today_start)
        yesterday_orders = count_orders_since(yesterday_start, today_start)

        today_deliveries = count_deliveries_since(today_start)
        yesterday_deliveries = count_deliveries_since(yesterday_start, today_start)

        total_deliveries = db.query(func.count(Delivery.delivery_id)).scalar() or 0
        pending_deliveries = db.query(func.count(Delivery.delivery_id)).filter(
            Delivery.delivery_status.in_(['OPEN', 'PICKING', 'SHIPPED', 'IN_TRANSIT'])
        ).scalar() or 0
        pending_share = (pending_deliveries / total_deliveries * 100) if total_deliveries else 0

        total_unpaid = db.query(
            func.sum(OpenAccountReceivable.receivable_amount - OpenAccountReceivable.received_amount)
        ).scalar() or 0

        month_profit = gross_profit_since(month_start)
        last_month_profit = gross_profit_since(last_month_start, month_start)

        return {
            "sales_orders": {
                "value": today_orders,
                "change": calc_change(today_orders, yesterday_orders),
                "type": "up" if today_orders >= yesterday_orders else "down",
                "comparison": "vs. Yesterday",
            },
            "delivery_orders": {
                "value": today_deliveries,
                "change": calc_change(today_deliveries, yesterday_deliveries),
                "type": "up" if today_deliveries >= yesterday_deliveries else "down",
                "comparison": "vs. Yesterday",
            },
            "pending_deliveries": {
                "value": pending_deliveries,
                "change": f"{pending_share:.1f}%",
                "type": "down" if pending_share <= 20 else "up",
                "comparison": "share of total",
            },
            "receivables": {
                "value": float(total_unpaid or 0),
                "change": "open",
                "type": "down" if not total_unpaid else "up",
                "comparison": "current outstanding",
            },
            "month_profit": {
                "value": month_profit,
                "change": calc_change(month_profit, last_month_profit),
                "type": "up" if month_profit >= last_month_profit else "down",
                "comparison": "vs. Last Month",
            },
        }

report_service = ReportService()
