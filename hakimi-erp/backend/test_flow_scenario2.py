"""Final scenario test on the seeded demo orders SO00101 / SO00102.

Run: D:/Anaconda/python.exe test_flow_scenario2.py
Mutates the dev DB (demo orders only).
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
        # A) full flow on a fresh order — every stage should execute
        show("A. SO00101 全流程", f.handle(db, "把 SO00101 从拣配一路跑到平帐"))

        # B) partial-pick drama on SO00102 (100 units total)
        show("B1. 先拣 50 件", f.handle(db, "先给 SO00102 拣 50 件"))
        show("B2. 确认拣配（应被拦下）", f.handle(db, "确认拣配 SO00102"))
        show("B3. 剩余全部拣完", f.handle(db, "把 SO00102 剩余的全部拣完"))
        show("B4. 接着跑到平帐", f.handle(db, "把 SO00102 从拣配一路跑到平帐"))
    finally:
        db.close()


if __name__ == "__main__":
    main()
