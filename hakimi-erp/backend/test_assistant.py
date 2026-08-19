"""Standalone smoke test for assistant_service (no server / DB needed).

Run from the backend directory:
    python test_assistant.py
"""

import asyncio
import json

from app.services import assistant_service


async def main() -> None:
    routes = assistant_service.known_routes()
    print(f"[1] route allowlist extracted: {len(routes)} routes")
    assert "/finance/unpaid" in routes
    assert "/sales/order/:id" not in routes  # parameterized routes excluded

    print("[2] calling Kimi API ...")
    result = await assistant_service.chat(
        message="我在哪里可以看到还没付款的应收账款？",
        history=[],
        current_path="/",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

    assert result["reply"], "reply must not be empty"
    if result["navigation"] is not None:
        assert result["navigation"]["route"] in routes
    print("[OK] smoke test passed")


if __name__ == "__main__":
    asyncio.run(main())
