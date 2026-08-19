"""Deterministic order-to-cash demo flow (no LLM involved).

Simulates an "AI agent" executing the chain

    sales order -> delivery -> start picking -> batch pick -> confirm
    -> ship -> post goods issue -> invoice -> receipt / settlement (平帐)

for demo purposes. The assistant endpoint pattern-matches the user message
with regular expressions, this module runs the real backend services, and a
pre-scripted answer (filled with the real document numbers / amounts) is
returned to the frontend. Nothing here calls an LLM.

Entry points used by the assistant endpoint:

- ``handle(db, message)``  -> reply dict, or None when the message does not
  match any scripted demo intent.
- ``guidance_reply()``     -> canned reply for unmatched messages, steering
  the user back onto the demo script.

Set ``FALLBACK_TO_LLM = True`` to let unmatched messages fall through to the
LLM assistant again (default False keeps the demo 100% deterministic).
"""

from __future__ import annotations

import re
import time
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.finance import Invoice, OpenAccountReceivable
from app.models.logistics import Delivery
from app.models.sales import SalesOrder
from app.schemas.finance import ReceiptCreate
from app.services.finance_service import finance_service
from app.services.logistics_service import logistics_service

# When False, messages that do not match a demo intent get the canned
# guidance reply instead of being forwarded to the LLM assistant.
FALLBACK_TO_LLM = False

# ---------------------------------------------------------------------------
# Intent matching
# ---------------------------------------------------------------------------

_SO_RE = re.compile(r"\bSO[-\s]?(\d{1,10})\b", re.IGNORECASE)
_QTY_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:件|个|台|套|箱|pcs?|PC)", re.IGNORECASE)

_PICK_WORDS = ("拣", "pick")
_SETTLE_WORDS = ("平帐", "平账", "清账", "清帐", "核销", "收款", "settle", "settlement")
_FULL_FLOW_HINTS = ("全流程", "全程", "一路", "一条龙", "一把梭", "端到端", "from pick", "order-to-cash", "order to cash")

INTENTS = ("full", "start", "pick", "confirm", "ship", "pgi", "invoice", "settle")


def _extract_so_id(message: str) -> Optional[str]:
    m = _SO_RE.search(message)
    if not m:
        return None
    return "SO" + m.group(1).zfill(5)


def _extract_qty(message: str) -> Optional[Decimal]:
    m = _QTY_RE.search(message)
    if not m:
        return None
    try:
        return Decimal(m.group(1))
    except Exception:
        return None


def match_intent(message: str) -> Optional[dict[str, Any]]:
    """Map a chat message to a scripted intent. Returns None when unmatched."""
    text = message.strip()
    if not text:
        return None
    low = text.lower()

    has_pick = any(w in low for w in _PICK_WORDS)
    has_settle = any(w in low for w in _SETTLE_WORDS)
    has_full_hint = any(w in low for w in _FULL_FLOW_HINTS)

    intent: Optional[str] = None
    # Order matters: more specific phrases first.
    if (has_pick and has_settle) or has_full_hint:
        intent = "full"
    elif "确认拣配" in text or "拣配确认" in text or "confirm pick" in low:
        intent = "confirm"
    elif "开始拣配" in text or "start pick" in low:
        intent = "start"
    elif has_pick:
        intent = "pick"
    elif "过账" in text or "过帐" in text or "pgi" in low or "goods issue" in low:
        intent = "pgi"
    elif "发货" in text or "发运" in text or "ship" in low:
        intent = "ship"
    elif "开票" in text or "开发票" in text or "发票" in text or "invoice" in low:
        intent = "invoice"
    elif has_settle:
        intent = "settle"

    if intent is None:
        return None
    return {
        "intent": intent,
        "so_id": _extract_so_id(text),
        "qty": _extract_qty(text),
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class StageBlocked(Exception):
    """A stage cannot run yet / is already done; carries a user-friendly note."""


def _mark_ran(ctx: dict[str, Any], stage: str) -> None:
    ctx.setdefault("ran", set()).add(stage)


def _step(steps: list[dict[str, str]], icon: str, text: str) -> None:
    steps.append({"icon": icon, "text": text})


def _money(value: Any) -> str:
    try:
        return f"¥{Decimal(str(value)):,.2f}"
    except Exception:
        return str(value)


def _qty_fmt(value: Any) -> str:
    """Format a Decimal quantity without trailing zeros (128.000 -> 128)."""
    try:
        d = Decimal(str(value))
        return str(d.quantize(Decimal("1")) if d == d.to_integral() else d.normalize())
    except Exception:
        return str(value)


def _find_so(db: Session, so_id: Optional[str]) -> SalesOrder:
    """Resolve the target sales order; fall back to an OPEN one.

    Fallback prefers OPEN orders that do not have a delivery yet, so the
    demo chain runs end-to-end for real instead of skipping every stage.
    """
    if so_id:
        so = db.query(SalesOrder).filter(SalesOrder.sales_order_id == so_id).first()
        if not so:
            raise StageBlocked(f"没有找到销售订单 {so_id}，请确认单号是否正确。")
        return so
    open_orders = (
        db.query(SalesOrder)
        .filter(SalesOrder.status == "OPEN")
        .order_by(SalesOrder.sales_order_id.desc())
        .all()
    )
    if not open_orders:
        raise StageBlocked("当前没有处于 OPEN 状态的销售订单，请先到销售管理创建一笔。")
    for so in open_orders:
        if _latest_delivery(db, so.sales_order_id) is None:
            return so
    return open_orders[0]


def _latest_delivery(db: Session, so_id: str) -> Optional[Delivery]:
    return (
        db.query(Delivery)
        .filter(Delivery.sales_order_id == so_id)
        .order_by(Delivery.delivery_id.desc())
        .first()
    )


def _get_delivery(db: Session, delivery_id: str) -> Delivery:
    d = db.query(Delivery).filter(Delivery.delivery_id == delivery_id).first()
    if not d:
        raise StageBlocked(f"没有找到发货单 {delivery_id}。")
    return d


def _remaining_map(delivery: Delivery) -> dict[str, Decimal]:
    out: dict[str, Decimal] = {}
    for item in delivery.items:
        remaining = Decimal(str(item.delivery_quantity or 0)) - Decimal(str(item.picked_quantity or 0))
        out[item.delivery_item_id] = remaining
    return out


def _plan_pick(delivery: Delivery, qty: Optional[Decimal]) -> dict[str, Decimal]:
    """Full pick of everything remaining, or spread ``qty`` across items."""
    plan: dict[str, Decimal] = {}
    budget = qty
    for item in delivery.items:
        remaining = Decimal(str(item.delivery_quantity or 0)) - Decimal(str(item.picked_quantity or 0))
        if remaining <= 0:
            continue
        take = remaining if budget is None else min(remaining, budget)
        if take <= 0:
            continue
        plan[item.delivery_item_id] = take
        if budget is not None:
            budget -= take
            if budget <= 0:
                break
    return plan


# --- individual stages ------------------------------------------------------

def _stage_ensure_delivery(db: Session, ctx: dict[str, Any]) -> None:
    steps: list[dict[str, str]] = ctx["steps"]
    so: SalesOrder = ctx["so"]
    delivery = _latest_delivery(db, so.sales_order_id)
    if delivery:
        ctx["delivery"] = delivery
        _step(steps, "⏭️", f"复用已有发货单 {delivery.delivery_id}（当前状态 {delivery.delivery_status}）")
        return
    created = logistics_service.create_from_sales_order(db, so.sales_order_id)
    # get_delivery_detail returns a plain dict despite its schema annotation.
    new_id = created["delivery_id"] if isinstance(created, dict) else created.delivery_id
    ctx["delivery"] = _get_delivery(db, new_id)
    n_items = len(ctx["delivery"].items)
    _mark_ran(ctx, "ensure")
    _step(steps, "📦", f"调用 create_from_sales_order → 创建发货单 {new_id}（{n_items} 个行项目）")


def _stage_start(db: Session, ctx: dict[str, Any]) -> None:
    steps = ctx["steps"]
    delivery: Delivery = ctx["delivery"]
    if delivery.delivery_status == "OPEN":
        logistics_service.start_picking(db, delivery.delivery_id)
        db.refresh(delivery)
        _mark_ran(ctx, "start")
        _step(steps, "✋", f"开始拣配 start_picking → 发货单状态 OPEN → PICKING")
    else:
        _step(steps, "⏭️", f"发货单已处于 {delivery.delivery_status}，跳过开始拣配")


def _stage_pick(db: Session, ctx: dict[str, Any]) -> None:
    steps = ctx["steps"]
    delivery: Delivery = ctx["delivery"]
    strict = ctx.get("strict", False)
    if delivery.delivery_status != "PICKING":
        if strict:
            raise StageBlocked(f"发货单当前状态为 {delivery.delivery_status}，无法记录拣配。")
        _step(steps, "⏭️", f"发货单状态为 {delivery.delivery_status}，跳过批次拣配")
        return
    plan = _plan_pick(delivery, ctx.get("qty"))
    if not plan:
        if strict:
            raise StageBlocked("所有行项目均已拣齐，可以直接确认拣配。")
        _step(steps, "⏭️", "所有行项目均已拣齐，跳过批次拣配")
        return
    logistics_service.pick_batch(db, delivery.delivery_id, plan, picked_by="AI Assistant")
    db.refresh(delivery)
    _mark_ran(ctx, "pick")
    total = sum(plan.values())
    remaining = sum(_remaining_map(delivery).values())
    if ctx.get("qty") is not None and remaining > 0:
        _step(steps, "🧺", f"批次拣配 pick_batch → 本批拣 {_qty_fmt(total)} 件，剩余 {_qty_fmt(remaining)} 件待拣")
    else:
        _step(steps, "🧺", f"批次拣配 pick_batch → 拣配 {len(plan)} 个行项目共 {_qty_fmt(total)} 件（已拣齐）")
    ctx["pick_remaining"] = remaining


def _stage_confirm(db: Session, ctx: dict[str, Any]) -> None:
    steps = ctx["steps"]
    delivery: Delivery = ctx["delivery"]
    if delivery.delivery_status == "PICKING":
        remaining = sum(_remaining_map(delivery).values())
        if remaining > 0:
            raise StageBlocked(f"还有 {_qty_fmt(remaining)} 件未拣齐，无法确认拣配。")
        logistics_service.confirm_picking(db, delivery.delivery_id)
        db.refresh(delivery)
        _mark_ran(ctx, "confirm")
        _step(steps, "✅", "确认拣配 confirm_picking → 状态 PICKING → SHIPPED")
    elif delivery.delivery_status == "OPEN":
        raise StageBlocked("这笔发货单还未开始拣配，需要先开始拣配并拣齐数量。")
    else:
        _step(steps, "⏭️", f"发货单已处于 {delivery.delivery_status}，跳过确认拣配")


def _stage_ship(db: Session, ctx: dict[str, Any]) -> None:
    steps = ctx["steps"]
    delivery: Delivery = ctx["delivery"]
    if delivery.delivery_status == "SHIPPED":
        logistics_service.ship_delivery(db, delivery.delivery_id)
        db.refresh(delivery)
        _mark_ran(ctx, "ship")
        _step(steps, "🚚", f"发货 ship_delivery → 状态 → IN_TRANSIT（跟踪号 {delivery.tracking_no}）")
    elif delivery.delivery_status in ("IN_TRANSIT", "PGI_DONE"):
        _step(steps, "⏭️", f"发货单已处于 {delivery.delivery_status}，跳过发货")
    else:
        raise StageBlocked(f"发货单当前状态为 {delivery.delivery_status}，需要先完成拣配确认才能发货。")


def _stage_pgi(db: Session, ctx: dict[str, Any]) -> None:
    steps = ctx["steps"]
    delivery: Delivery = ctx["delivery"]
    if delivery.delivery_status == "IN_TRANSIT":
        logistics_service.post_goods_issue(db, delivery.delivery_id)
        db.refresh(delivery)
        _mark_ran(ctx, "pgi")
        _step(steps, "📤", "过账 post_goods_issue → 状态 → PGI_DONE，库存已扣减")
    elif delivery.delivery_status == "PGI_DONE":
        _step(steps, "⏭️", "PGI 已过账，跳过")
    else:
        raise StageBlocked(f"发货单当前状态为 {delivery.delivery_status}，需要先发货（IN_TRANSIT）才能过账。")


def _stage_invoice(db: Session, ctx: dict[str, Any]) -> None:
    steps = ctx["steps"]
    delivery: Delivery = ctx["delivery"]
    existing = db.query(Invoice).filter(Invoice.delivery_id == delivery.delivery_id).first()
    if existing:
        ctx["invoice"] = existing
        _step(steps, "⏭️", f"发票已存在（{existing.invoice_id}），跳过开票")
        return
    if delivery.delivery_status != "PGI_DONE":
        raise StageBlocked(f"发货单当前状态为 {delivery.delivery_status}，需要 PGI 完成后才能开票。")
    invoice = finance_service.create_invoice_from_delivery(db, delivery.delivery_id)
    ctx["invoice"] = invoice
    _mark_ran(ctx, "invoice")
    _step(steps, "🧾", f"开票 create_invoice_from_delivery → 发票 {invoice.invoice_id}，金额 {_money(invoice.total_amount)}（含 13% 税）")


def _stage_settle(db: Session, ctx: dict[str, Any]) -> None:
    steps = ctx["steps"]
    so: SalesOrder = ctx["so"]
    invoice = ctx.get("invoice")
    if invoice is None:
        invoice = (
            db.query(Invoice)
            .filter(Invoice.sales_order_id == so.sales_order_id)
            .order_by(Invoice.invoice_id.desc())
            .first()
        )
    if invoice is None:
        raise StageBlocked("该订单还没有发票，需要先完成开票。")
    ctx["invoice"] = invoice

    ar = db.query(OpenAccountReceivable).filter(OpenAccountReceivable.invoice_id == invoice.invoice_id).first()
    if ar is None:
        if invoice.status == "CLEARED":
            _step(steps, "⏭️", f"发票 {invoice.invoice_id} 已平帐（CLEARED），无需重复收款")
            return
        raise StageBlocked(f"发票 {invoice.invoice_id} 没有未清应收记录（状态 {invoice.status}）。")

    amount = Decimal(str(ar.receivable_amount)) - Decimal(str(ar.received_amount or 0))
    if amount <= 0:
        _step(steps, "⏭️", "应收余额为 0，无需收款")
        return
    receipt = finance_service.post_receipt(db, ReceiptCreate(
        invoice_id=invoice.invoice_id,
        receipt_amount=amount,
        payment_method="Bank Transfer",
        currency=invoice.currency or "CNY",
        remark="AI assistant demo settlement",
    ))
    ctx["receipt"] = receipt
    _mark_ran(ctx, "settle")
    _step(steps, "💰", f"收款平帐 post_receipt → 收款单 {receipt.receipt_id}，{_money(amount)} 全额核销；应收关闭、销售订单关闭")


# --- runners -----------------------------------------------------------------

_ALL_STAGES = [
    ("ensure", _stage_ensure_delivery),
    ("start", _stage_start),
    ("pick", _stage_pick),
    ("confirm", _stage_confirm),
    ("ship", _stage_ship),
    ("pgi", _stage_pgi),
    ("invoice", _stage_invoice),
    ("settle", _stage_settle),
]

_SINGLE_STAGE = {
    "start": ["ensure", "start"],
    "pick": ["ensure", "start", "pick"],
    "confirm": ["ensure", "confirm"],
    "ship": ["ensure", "ship"],
    "pgi": ["ensure", "pgi"],
    "invoice": ["ensure", "invoice"],
    "settle": ["ensure", "settle"],
}

_NEXT_SUGGESTION = {
    "start": "批次拣配 {so}",
    "pick": "确认拣配 {so}",
    "confirm": "发货 {so}",
    "ship": "发货过账 {so}",
    "pgi": "开票 {so}",
    "invoice": "收款平帐 {so}",
}

_STAGE_LABEL = {
    "start": "开始拣配",
    "pick": "批次拣配",
    "confirm": "确认拣配",
    "ship": "发货",
    "pgi": "发货过账",
    "invoice": "开票",
    "settle": "收款平帐",
}

_STAGE_REPLY = {
    "start": "已开始拣配，发货单进入 PICKING 状态。",
    "pick": "批次拣配已记录。",
    "confirm": "拣配已确认，可以安排发货了。",
    "ship": "已发货，货物在途。",
    "pgi": "发货过账完成，库存已扣减，可以开票了。",
    "invoice": "发票已开具，应收已挂账。",
    "settle": "收款核销完成，这笔订单已经平帐。",
}


def _finalize(ctx: dict[str, Any], intent: str, blocked_note: Optional[str] = None) -> dict[str, Any]:
    so: SalesOrder = ctx["so"]
    steps = ctx["steps"]
    so_id = so.sales_order_id

    if blocked_note:
        _step(steps, "⏸️", blocked_note)
        reply = f"执行暂停：{blocked_note}"
        suggestions = [f"把 {so_id} 剩余的全部拣完", f"把 {so_id} 从拣配一路跑到平帐"]
        return {"reply": reply, "steps": steps, "navigation": None, "suggestions": suggestions}

    receipt = ctx.get("receipt")
    invoice = ctx.get("invoice")
    if intent == "full" and receipt is not None:
        reply = (
            f"销售订单 {so_id} 已完成「拣配 → 发货 → 过账 → 开票 → 收款平帐」全流程：\n"
            f"发票 {invoice.invoice_id}（{_money(invoice.total_amount)}）已全额核销，应收关闭，订单状态 CLOSED。"
        )
        navigation = {"label": "应收管理", "route": "/finance/receivables"}
        suggestions = [
            "随便挑一笔开放订单跑全流程",
            "先给另一笔订单拣 50 件",
        ]
    elif intent == "full":
        reply = f"订单 {so_id} 的全流程已推进到当前可达状态，明细见上方步骤。"
        navigation = {"label": "发货单列表", "route": "/delivery/list"}
        suggestions = [f"把 {so_id} 从拣配一路跑到平帐"]
    else:
        ran = ctx.get("ran", set())
        if intent in ran:
            reply = _STAGE_REPLY.get(intent, "已完成。")
        else:
            # Single-step command whose stage was only skipped: say so
            # honestly instead of claiming the action just happened.
            reply = (
                f"订单 {so_id} 的「{_STAGE_LABEL.get(intent, intent)}」此前已经完成，"
                "本次无需重复执行（当前进度见上方步骤）。"
            )
        navigation = None
        nxt = _NEXT_SUGGESTION.get(intent)
        suggestions = [nxt.format(so=so_id)] if nxt else [f"把 {so_id} 从拣配一路跑到平帐"]

    return {"reply": reply, "steps": steps, "navigation": navigation, "suggestions": suggestions}


def _run_stage(db: Session, ctx: dict[str, Any], fn) -> None:
    """Run one stage; retry once on timestamp-id primary-key collisions.

    The underlying services generate document ids with second precision
    (``DEL%y%m%d%H%M%S`` etc.), so two documents created within the same
    second collide on the primary key. Rolling back and retrying in the next
    second resolves it; stages are state-guarded and therefore safe to
    re-enter after a rollback.
    """
    from sqlalchemy.exc import IntegrityError

    try:
        fn(db, ctx)
    except IntegrityError:
        db.rollback()
        time.sleep(1.05)
        fn(db, ctx)


# --- plan / confirm / execute ----------------------------------------------

_CONFIRM_WORDS = ("确认执行", "确认", "执行", "confirm", "execute", "yes")
_CANCEL_WORDS = ("取消", "cancel", "算了", "不用了", "先不")
_NUM_ICONS = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣")


def _so_totals(so: SalesOrder) -> tuple[Decimal, Decimal]:
    """(total order quantity, estimated gross amount incl. 13% tax)."""
    total_qty = Decimal(0)
    est = Decimal(0)
    for item in so.items:
        q = Decimal(str(item.order_quantity or 0))
        p = Decimal(str(item.unit_price or 0))
        total_qty += q
        est += p * q
    return total_qty, est * Decimal("1.13")


def _plan_lines(db: Session, so: SalesOrder, delivery: Optional[Delivery],
                intent: str, qty: Optional[Decimal]) -> list[str]:
    """Human-readable preview of what a command would do (read-only)."""
    n_items = len(so.items)
    total_qty, est = _so_totals(so)

    if delivery is not None:
        base = f"复用发货单 {delivery.delivery_id}（当前状态 {delivery.delivery_status}），从当前进度继续执行"
    else:
        base = f"依据订单创建发货单（{n_items} 个行项目，共 {_qty_fmt(total_qty)} 件）"

    if intent == "full":
        return [
            base,
            "开始拣配，并批次拣配全部剩余数量",
            "确认拣配 → 发货 → 发货过账（PGI），扣减库存",
            f"依据发货单开具发票并挂应收（按订单价格预估 {_money(est)}，含 13% 税）",
            "对发票全额收款核销：应收关闭、发票结清、销售订单关闭",
        ]
    if intent == "start":
        lines = [] if delivery is not None else [base]
        return lines + ["开始拣配：发货单状态 OPEN → PICKING"]
    if intent == "pick":
        lines = []
        if delivery is None:
            lines.append(f"{base}，并开始拣配")
        elif delivery.delivery_status == "OPEN":
            lines.append("开始拣配（发货单 OPEN → PICKING）")
        if qty is not None:
            lines.append(f"批次拣配 {_qty_fmt(qty)} 件（超出剩余数量时按剩余量拣）")
        else:
            rem = f"（{_qty_fmt(sum(_remaining_map(delivery).values()))} 件）" if delivery is not None else ""
            lines.append(f"批次拣配全部剩余数量{rem}")
        return lines
    if intent == "confirm":
        extra = ""
        if delivery is not None:
            picked = sum(Decimal(str(i.picked_quantity or 0)) for i in delivery.items)
            needed = sum(Decimal(str(i.delivery_quantity or 0)) for i in delivery.items)
            extra = f"（当前已拣 {_qty_fmt(picked)}/{_qty_fmt(needed)} 件）"
        return [f"确认拣配：要求全部行项目拣齐{extra}，确认后状态 PICKING → SHIPPED"]
    if intent == "ship":
        return ["发货：状态 SHIPPED → IN_TRANSIT，生成承运商与跟踪号"]
    if intent == "pgi":
        return ["发货过账：状态 IN_TRANSIT → PGI_DONE，扣减库存"]
    if intent == "invoice":
        return [f"依据发货单开具发票并挂应收（按订单价格预估 {_money(est)}，含 13% 税）"]
    # settle
    invoice = (
        db.query(Invoice)
        .filter(Invoice.sales_order_id == so.sales_order_id)
        .order_by(Invoice.invoice_id.desc())
        .first()
    )
    if invoice is not None:
        ar = db.query(OpenAccountReceivable).filter(OpenAccountReceivable.invoice_id == invoice.invoice_id).first()
        if ar is not None:
            remaining = Decimal(str(ar.receivable_amount)) - Decimal(str(ar.received_amount or 0))
            return [f"对发票 {invoice.invoice_id} 全额收款核销 {_money(remaining)}：应收关闭、发票结清、销售订单关闭"]
        return [f"发票 {invoice.invoice_id} 无未清应收，无需收款（将如实跳过）"]
    return ["对发票全额收款核销（该订单尚无发票，执行时将如实提示）"]


def _error_reply(text: str) -> dict[str, Any]:
    return {
        "reply": text,
        "steps": [],
        "navigation": {"label": "销售订单", "route": "/sales/orders"},
        "suggestions": ["随便挑一笔开放订单跑全流程"],
    }


def _plan(db: Session, intent: str, so_id: Optional[str], qty: Optional[Decimal]) -> dict[str, Any]:
    """Build a read-only execution plan and ask the user to confirm."""
    try:
        so = _find_so(db, so_id)
    except StageBlocked as exc:
        return _error_reply(str(exc))

    delivery = _latest_delivery(db, so.sales_order_id)
    steps: list[dict[str, str]] = []
    label = "拣配 → 发货 → 开票 → 平帐 全流程" if intent == "full" else f"单步操作：{_STAGE_LABEL.get(intent, intent)}"
    _step(steps, "🔍", f"识别指令：对销售订单 {so.sales_order_id} 执行{label}"
           + (f"（本批 {_qty_fmt(qty)} 件）" if qty else ""))
    _step(steps, "📄", f"找到销售订单 {so.sales_order_id}（客户 {so.customer_id}，净值 {_money(so.net_value)}，状态 {so.status}）")
    for i, line in enumerate(_plan_lines(db, so, delivery, intent, qty)):
        _step(steps, _NUM_ICONS[i] if i < len(_NUM_ICONS) else "▫️", line)

    return {
        "reply": "以上是执行计划。操作将真实修改业务数据，确认后我立即执行。",
        "steps": steps,
        "navigation": None,
        "suggestions": [],
        "pending_action": {
            "intent": intent,
            "so_id": so.sales_order_id,
            "qty": str(qty) if qty is not None else None,
        },
    }


def _execute(db: Session, intent: str, so_id: Optional[str], qty: Optional[Decimal]) -> dict[str, Any]:
    """Run a confirmed action through the state-guarded stage chain."""
    try:
        so = _find_so(db, so_id)
    except StageBlocked as exc:
        return _error_reply(str(exc))

    ctx: dict[str, Any] = {
        "so": so,
        "steps": [],
        "qty": qty,
        # single-step commands report "already done / not ready" as a blocked
        # note; the full flow skips completed stages and keeps going.
        "strict": intent != "full",
    }
    steps = ctx["steps"]

    label = "拣配 → 发货 → 开票 → 平帐 全流程" if intent == "full" else f"单步操作：{_STAGE_LABEL.get(intent, intent)}"
    _step(steps, "✅", "用户已确认，开始执行")
    _step(steps, "🔍", f"执行内容：对销售订单 {so.sales_order_id} {label}"
           + (f"（本批 {_qty_fmt(qty)} 件）" if qty else ""))
    _step(steps, "📄", f"找到销售订单 {so.sales_order_id}（客户 {so.customer_id}，净值 {_money(so.net_value)}，状态 {so.status}）")

    stage_names = [name for name, _ in _ALL_STAGES] if intent == "full" else _SINGLE_STAGE[intent]
    stage_map = dict(_ALL_STAGES)

    blocked: Optional[str] = None
    try:
        for name in stage_names:
            _run_stage(db, ctx, stage_map[name])
    except StageBlocked as exc:
        blocked = str(exc)
    except Exception as exc:  # service-layer business errors
        db.rollback()  # a failed flush poisons the session; reset it
        blocked = f"系统返回：{exc}"

    return _finalize(ctx, intent, blocked)


def handle(db: Session, message: str, pending_action: Any = None) -> Optional[dict[str, Any]]:
    """Try to handle a chat message as a scripted order-to-cash demo command.

    Two-phase protocol: a matched command first returns a read-only plan with
    a ``pending_action`` payload; the frontend echoes that payload back
    together with a confirm word to actually execute. State is re-validated
    at execution time by the stage guards, so a stale plan can never do
    anything the current data does not allow.

    Returns the reply contract dict, or None when the message does not match
    any demo intent (caller decides: guidance reply or LLM fallback).
    """
    if pending_action is not None and match_intent(message) is None:
        # A new command supersedes the pending plan; only react to explicit
        # confirm / cancel words here.
        low = message.strip().lower()
        if any(w in low for w in _CANCEL_WORDS):
            return {
                "reply": "好的，已取消该操作，未修改任何业务数据。",
                "steps": [],
                "navigation": None,
                "suggestions": ["随便挑一笔开放订单跑全流程"],
            }
        if any(w in low for w in _CONFIRM_WORDS):
            try:
                intent = pending_action.intent
                if intent not in INTENTS:
                    raise ValueError(f"unknown intent {intent}")
                qty = Decimal(pending_action.qty) if pending_action.qty else None
            except Exception:
                return _error_reply("待确认的操作已失效，请重新下达指令。")
            return _execute(db, intent, pending_action.so_id, qty)

    matched = match_intent(message)
    if matched is None:
        return None

    return _plan(db, matched["intent"], matched["so_id"], matched.get("qty"))


def guidance_reply() -> dict[str, Any]:
    """Canned reply for messages outside the demo script."""
    return {
        "reply": (
            "我是订单到收款（Order-to-Cash）流程助手，可以直接帮你把销售订单"
            "从拣配一路执行到收款平帐。只要告诉我订单号即可，例如：\n"
            "「把 SO00107 从拣配一路跑到平帐」\n"
            "也可以分步来：开始拣配 → 批次拣配 → 确认拣配 → 发货 → 过账 → 开票 → 收款平帐。"
        ),
        "steps": [],
        "navigation": None,
        "suggestions": [
            "随便挑一笔开放订单跑全流程",
            "把 SO00107 从拣配一路跑到平帐",
            "先给 SO00108 拣 50 件",
        ],
    }
