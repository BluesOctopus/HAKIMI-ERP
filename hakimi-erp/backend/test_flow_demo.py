"""Quick verification for the deterministic order-to-cash demo flow.

Run with the project Python (D:/Anaconda/python.exe test_flow_demo.py).
Covers: intent regex matching + a full end-to-end run against the dev DB.
"""

from app.core.database import SessionLocal
from app.services.flows import order_to_cash as f


def test_intents():
    msgs = [
        "把 SO00001 从拣配一路跑到平帐",
        "先给 SO00002 拣 50 件",
        "随便挑一笔开放订单跑全流程",
        "确认拣配 SO00001",
        "发货 SO1",
        "开票 so00003",
        "收款平帐 SO00001",
        "把 SO00001 剩余的全部拣完",
        "开始拣配 SO00004",
        "你好，今天天气怎么样",
    ]
    for m in msgs:
        print(repr(m), "->", f.match_intent(m))


def test_full_flow():
    db = SessionLocal()
    try:
        result = f.handle(db, "随便挑一笔开放订单跑全流程")
        print("\n--- reply ---")
        print(result["reply"])
        print("--- steps ---")
        for s in result["steps"]:
            print(s["icon"], s["text"])
        print("--- navigation ---", result["navigation"])
        print("--- suggestions ---", result["suggestions"])
    finally:
        db.close()


if __name__ == "__main__":
    test_intents()
    test_full_flow()
