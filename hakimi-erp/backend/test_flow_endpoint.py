"""Endpoint-level smoke test for the demo flow (auth + dispatch + schema).

Run: D:/Anaconda/python.exe test_flow_endpoint.py
Uses FastAPI TestClient in-process; no server needed.
Only runs non-mutating commands (guidance + already-done single step).
"""

from fastapi.testclient import TestClient

from app.main import app

USER = {"username": "flow_tester", "email": "flow_tester@example.com",
        "password": "Test1234!", "full_name": "Flow Tester"}


def get_token(c: TestClient) -> str:
    r = c.post("/api/v1/auth/register", json=USER)
    if r.status_code == 201:
        return r.json()["data"]["access_token"]
    r = c.post("/api/v1/auth/login",
               json={"account": USER["username"], "password": USER["password"]})
    r.raise_for_status()
    return r.json()["data"]["access_token"]


def main():
    c = TestClient(app)
    token = get_token(c)
    headers = {"Authorization": f"Bearer {token}"}

    # 1) unmatched -> canned guidance (no LLM)
    r = c.post("/api/v1/assistant/chat", headers=headers,
               json={"message": "你好，系统怎么用？", "history": []})
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    print("unmatched reply:", d["reply"][:40], "...")
    print("unmatched suggestions:", d["suggestions"])
    assert d["steps"] == []

    # 2) matched single-step on a pre-settled seed order -> honest 'already done'
    r = c.post("/api/v1/assistant/chat", headers=headers,
               json={"message": "确认拣配 SO00001", "history": []})
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    print("\nmatched reply:", d["reply"])
    for s in d["steps"]:
        print("  ", s["icon"], s["text"])
    print("suggestions:", d["suggestions"])

    print("\n[SMOKE OK]")


if __name__ == "__main__":
    main()
