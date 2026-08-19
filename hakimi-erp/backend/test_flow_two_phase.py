"""Two-phase (plan -> confirm -> execute) test for the demo flow.

Run: D:/Anaconda/python.exe test_flow_two_phase.py
Mutates the dev DB (demo orders SO00105 / SO00106 only).
"""

from app.core.database import SessionLocal
from app.models.logistics import Delivery
from app.models.sales import SalesOrder
from app.services.flows import order_to_cash as f


class Action:
    """Mimics the PendingAction pydantic model the endpoint passes in."""

    def __init__(self, d):
        self.intent = d["intent"]
        self.so_id = d["so_id"]
        self.qty = d["qty"]


def show(tag, result):
    print(f"\n===== {tag} =====")
    for s in result["steps"]:
        print(" ", s["icon"], s["text"])
    print("REPLY:", result["reply"])
    print("PENDING:", result.get("pending_action"))
    print("SUGGESTIONS:", result["suggestions"])


def main():
    db = SessionLocal()
    try:
        # 1) plan only — nothing must be created yet
        r = f.handle(db, "把 SO00106 从拣配一路跑到平帐")
        show("1. 下指令 → 只出计划", r)
        assert r.get("pending_action"), "plan must carry pending_action"
        assert db.query(Delivery).filter(Delivery.sales_order_id == "SO00106").first() is None, \
            "plan phase must not create a delivery"
        so = db.query(SalesOrder).filter(SalesOrder.sales_order_id == "SO00106").first()
        assert so.status == "OPEN", "plan phase must not touch the order"
        print(">> 计划阶段未修改任何数据 ✓")

        # 2) confirm -> real execution
        r = f.handle(db, "确认执行", Action(r["pending_action"]))
        show("2. 确认执行 → 全链路真实执行", r)
        so = db.query(SalesOrder).filter(SalesOrder.sales_order_id == "SO00106").first()
        assert so.status == "CLOSED", "order should be closed after full flow"
        print(">> 确认后全链路执行完成，订单 CLOSED ✓")

        # 3) partial-pick drama on SO00105
        r = f.handle(db, "先给 SO00105 拣 50 件")
        show("3. 部分拣配 → 计划", r)
        r = f.handle(db, "确认执行", Action(r["pending_action"]))
        show("3b. 确认 → 拣 50 件", r)
        r = f.handle(db, "确认拣配 SO00105")
        show("3c. 确认拣配 → 计划（提示未拣齐）", r)
        r = f.handle(db, "确认执行", Action(r["pending_action"]))
        show("3d. 确认 → 被业务规则拦下", r)
        r = f.handle(db, "把 SO00105 剩余的全部拣完")
        r = f.handle(db, "确认执行", Action(r["pending_action"]))
        show("3e. 拣完剩余", r)

        # 4) a new command supersedes a pending plan
        r = f.handle(db, "开票 SO00105")
        assert r.get("pending_action"), "invoice plan expected"
        r2 = f.handle(db, "随便挑一笔开放订单跑全流程", Action(r["pending_action"]))
        show("4. 挂起计划时下达新指令 → 新指令优先", r2)
        assert r2.get("pending_action"), "new command should produce a new plan"

        # 5) cancel
        r = f.handle(db, "取消", Action(r2["pending_action"]))
        show("5. 取消", r)
    finally:
        db.close()


if __name__ == "__main__":
    main()
