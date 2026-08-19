"""In-app AI assistant service.

Loads the product context document (app/assistant/context.md) and calls an
OpenAI-compatible LLM API (Kimi / Moonshot) to answer navigation and feature
questions about the HAKIMI ERP website.

This module intentionally has no FastAPI imports so it can be tested
standalone.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings

CONTEXT_PATH = Path(__file__).resolve().parent.parent / "assistant" / "context.md"

# Reply contract returned to the frontend (see context.md section 8).
OUTPUT_INSTRUCTION = """
You must answer with a single JSON object and nothing else, in this exact shape:

{
  "reply": "your short answer to the user, in the user's language",
  "navigation": {"label": "Page Name", "route": "/some/route"} or null,
  "suggestions": ["optional follow-up question 1", "optional follow-up question 2"]
}

Rules:
- "navigation" must be null unless the user would benefit from being taken to
  a specific page. Only use routes that appear in the context document.
- Keep "reply" short and practical.
- Do not wrap the JSON in markdown code fences.
""".strip()

_cached_context: str | None = None
_cached_routes: set[str] | None = None


def load_context(force_reload: bool = False) -> str:
    """Load the assistant context document (cached after first read)."""
    global _cached_context
    if _cached_context is None or force_reload:
        _cached_context = CONTEXT_PATH.read_text(encoding="utf-8")
    return _cached_context


def known_routes() -> set[str]:
    """Extract the route allowlist from the context document.

    Routes are the backtick-quoted paths like `/sales/orders` in context.md,
    so the allowlist stays in sync with the document automatically.
    """
    global _cached_routes
    if _cached_routes is None:
        routes = set(re.findall(r"`(/[A-Za-z0-9/_:.-]+)`", load_context()))
        # Parameterized routes like /sales/order/:id are not navigable as-is.
        _cached_routes = {r for r in routes if ":" not in r}
    return _cached_routes


def _build_messages(
    message: str,
    history: list[dict[str, str]] | None,
    current_path: str | None,
) -> list[dict[str, str]]:
    system = load_context() + "\n\n---\n\n" + OUTPUT_INSTRUCTION
    if current_path:
        system += f"\n\nThe user is currently viewing page: {current_path}"

    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    for item in (history or [])[-20:]:  # keep the request small
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})
    return messages


def _parse_reply(raw: str) -> dict[str, Any]:
    """Parse the model output into the reply contract, with safe fallbacks."""
    text = raw.strip()
    # Tolerate accidental markdown fences around the JSON.
    fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Fall back to a plain-text reply instead of failing the request.
        return {"reply": raw.strip(), "navigation": None, "suggestions": []}

    reply = data.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        reply = raw.strip()

    navigation = data.get("navigation")
    if isinstance(navigation, dict):
        route = navigation.get("route")
        label = navigation.get("label")
        if isinstance(route, str) and route in known_routes():
            navigation = {
                "label": label if isinstance(label, str) and label else route,
                "route": route,
            }
        else:
            navigation = None
    else:
        navigation = None

    suggestions = data.get("suggestions")
    if not isinstance(suggestions, list):
        suggestions = []
    suggestions = [s for s in suggestions if isinstance(s, str) and s][:3]

    return {"reply": reply, "navigation": navigation, "suggestions": suggestions}


async def chat(
    message: str,
    history: list[dict[str, str]] | None = None,
    current_path: str | None = None,
) -> dict[str, Any]:
    """Send one assistant turn to the LLM and return the reply contract."""
    if not settings.LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY is not configured")

    payload = {
        "model": settings.LLM_MODEL,
        "messages": _build_messages(message, history, current_path),
        "max_tokens": settings.LLM_MAX_TOKENS,
        # kimi-k2.6 is a hybrid thinking model; keep latency low for chat.
        "thinking": {"type": "disabled"},
    }
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
        resp = await client.post(
            f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        body = resp.json()

    raw = body["choices"][0]["message"]["content"]
    return _parse_reply(raw)
