"""Scenario test: step-by-step partial-pick script + idempotent re-run.

Run with the project Python (D:/Anaconda/python.exe test_flow_scenario.py).
Mutates the dev DB (demo data only).
"""

from app.core.database import SessionLocal
from app.services.flows import order_to_cash as f


def show(tag, result):
    print(f"\n===== {tag} =====")
    for s in result["steps"]:
        print(" ", s["icon"], s["text"])
    print("REPLY:", result["reply"])
    print("SUGGESTIONS:", result["suggestions"])


def main():
    db = SessionLocal()
    try:
        # pick a currently OPEN order for the step-by-step script
        from app.models.sales import SalesOrder
        so = (
            db.query(SalesOrder)
            .filter(SalesOrder.status == "OPEN")
            .order_by(SalesOrder.sales_order_id.desc())
            .first()
        )
        if not so:
            print("No OPEN sales order left; scenario skipped.")
            return
        so_id = so.sales_order_id
        print(f"Target order: {so_id}")

        show("1. 部分拣配 50 件", f.handle(db, f"先给 {so_id} 拣 50 件"))
        show("2. 确认拣配（应被拦下）", f.handle(db, f"确认拣配 {so_id}"))
        show("3. 拣完剩余", f.handle(db, f"把 {so_id} 剩余的全部拣完"))
        show("4. 确认拣配", f.handle(db, f"确认拣配 {so_id}"))
        show("5. 发货", f.handle(db, f"发货 {so_id}"))
        show("6. 过账", f.handle(db, f"发货过账 {so_id}"))
        show("7. 开票", f.handle(db, f"开票 {so_id}"))
        show("8. 收款平帐", f.handle(db, f"收款平帐 {so_id}"))
        show("9. 重复跑全流程（幂等）", f.handle(db, f"把 {so_id} 从拣配一路跑到平帐"))
        show("10. 未命中引导", f.guidance_reply())
    finally:
        db.close()


if __name__ == "__main__":
    main()
