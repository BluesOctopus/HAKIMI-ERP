"""Sweep common GET endpoints to find 500s."""

import subprocess
import sys
import time

import httpx

BASE = "http://localhost:8000"

ENDPOINTS = [
    "/api/v1/master/partners/",
    "/api/v1/master/materials/",
    "/api/v1/master/materials/pricing-conditions",
    "/api/v1/master/materials/sales-organizations",
    "/api/v1/sales/inquiries",
    "/api/v1/sales/quotations",
    "/api/v1/sales/orders",
    "/api/v1/logistics/deliveries",
    "/api/v1/logistics/storage-locations",
    "/api/v1/finance/invoices",
    "/api/v1/finance/ar/open",
    "/api/v1/finance/ar/closed",
    "/api/v1/finance/receipts",
    "/api/v1/reports/sales-performance",
    "/api/v1/reports/financial-summary",
    "/api/v1/reports/financial-detail",
    "/api/v1/reports/delivery-stats",
    "/api/v1/reports/dashboard-summary",
]


def wait_for_server(client: httpx.Client, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if client.get(f"{BASE}/").status_code == 200:
                return
        except httpx.ConnectError:
            pass
        time.sleep(0.5)
    raise RuntimeError("backend did not become ready")


def main() -> int:
    log = open("sweep_server.log", "w", encoding="utf-8")
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    try:
        with httpx.Client(timeout=60.0) as client:
            wait_for_server(client)
            resp = client.post(
                f"{BASE}/api/v1/auth/login",
                json={"account": "e2e_tester", "password": "Test1234!"},
            )
            token = resp.json()["data"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            failures = []
            for path in ENDPOINTS:
                resp = client.get(f"{BASE}{path}", headers=headers)
                status = resp.status_code
                print(f"{status} {path}")
                if status >= 400:
                    failures.append((path, status, resp.text[:300]))

        server.terminate()
        server.wait(timeout=10)
        log.close()
        with open("sweep_server.log", encoding="utf-8", errors="replace") as f:
            text = f.read()

        if failures:
            print("\n=== failures ===")
            for path, status, body in failures:
                print(f"\n{status} {path}\n  {body}")
            # print first traceback block from server log
            idx = text.find("Traceback")
            if idx >= 0:
                print("\n--- first server traceback ---")
                print(text[idx : idx + 2000])
        else:
            print("\nno failures found")
        return 0
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
        print("[cleanup] backend stopped")


if __name__ == "__main__":
    sys.exit(main())
