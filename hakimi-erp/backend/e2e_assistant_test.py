"""One-shot end-to-end test: start backend, register, login, chat, stop backend.

Run from the backend directory:
    python e2e_assistant_test.py

The script always terminates the uvicorn process it started.
"""

import json
import subprocess
import sys
import time

import httpx

BASE = "http://localhost:8000"
TEST_USER = {
    "username": "e2e_tester",
    "email": "e2e_tester@example.com",
    "password": "Test1234!",
    "full_name": "E2E Tester",
}


def wait_for_server(client: httpx.Client, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = client.get(f"{BASE}/")
            if resp.status_code == 200:
                return
        except httpx.ConnectError:
            pass
        time.sleep(0.5)
    raise RuntimeError("backend did not become ready in time")


def main() -> int:
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        with httpx.Client(timeout=120.0) as client:
            print("[1] waiting for backend ...")
            wait_for_server(client)
            print("    backend is up")

            print("[2] registering test user ...")
            resp = client.post(f"{BASE}/api/v1/auth/register", json=TEST_USER)
            if resp.status_code == 201:
                token = resp.json()["data"]["access_token"]
                print("    registered, got token")
            elif resp.status_code == 400 and "exist" in resp.text.lower():
                print("    user already exists, logging in instead")
                resp = client.post(
                    f"{BASE}/api/v1/auth/login",
                    json={"account": TEST_USER["username"], "password": TEST_USER["password"]},
                )
                resp.raise_for_status()
                token = resp.json()["data"]["access_token"]
            else:
                raise RuntimeError(f"register failed: {resp.status_code} {resp.text}")

            headers = {"Authorization": f"Bearer {token}"}

            print("[3] chat without auth should be rejected ...")
            resp = client.post(f"{BASE}/api/v1/assistant/chat", json={"message": "hi", "history": []})
            assert resp.status_code in (401, 403), f"expected 401/403, got {resp.status_code}"
            print(f"    OK ({resp.status_code})")

            print("[4] asking the assistant a navigation question ...")
            resp = client.post(
                f"{BASE}/api/v1/assistant/chat",
                headers=headers,
                json={
                    "message": "Where can I create a new sales order?",
                    "history": [],
                    "current_path": "/",
                },
            )
            resp.raise_for_status()
            data = resp.json()["data"]
            print(json.dumps(data, ensure_ascii=False, indent=2))
            assert data["reply"], "empty reply"
            if data.get("navigation"):
                print(f"    navigation -> {data['navigation']['route']}")

            print("[5] follow-up turn with history ...")
            resp = client.post(
                f"{BASE}/api/v1/assistant/chat",
                headers=headers,
                json={
                    "message": "And where do I see the unpaid receivables?",
                    "history": [
                        {"role": "user", "content": "Where can I create a new sales order?"},
                        {"role": "assistant", "content": data["reply"]},
                    ],
                    "current_path": "/sales/orders",
                },
            )
            resp.raise_for_status()
            data2 = resp.json()["data"]
            print(json.dumps(data2, ensure_ascii=False, indent=2))
            assert data2["reply"], "empty reply on follow-up"

        print("\n[E2E OK] all checks passed")
        return 0
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
        print("[cleanup] backend stopped")


if __name__ == "__main__":
    sys.exit(main())
