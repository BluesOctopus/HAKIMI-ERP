from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.assistant import ChatReply, ChatRequest
from app.schemas.base import ResponseModel
from app.services import assistant_service
from app.services.flows import order_to_cash

router = APIRouter()


@router.post("/chat", response_model=ResponseModel[ChatReply])
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """In-app assistant chat endpoint.

    Demo commands for the order-to-cash flow (picking -> settlement) are
    handled deterministically by the scripted flow engine (no LLM involved);
    other messages fall back to canned guidance, or to the LLM assistant when
    order_to_cash.FALLBACK_TO_LLM is enabled.
    """
    # 1) Scripted demo flow (deterministic, mutates business data for demo).
    #    Two-phase: commands return a plan + pending_action first; execution
    #    only happens when the client echoes pending_action with a confirm.
    try:
        result = order_to_cash.handle(db, request.message, request.pending_action)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Demo flow failed: {exc}") from exc
    if result is not None:
        return ResponseModel(data=ChatReply(**result))

    # 2) Unmatched: canned guidance by default; LLM only if explicitly enabled.
    if not order_to_cash.FALLBACK_TO_LLM:
        return ResponseModel(data=ChatReply(**order_to_cash.guidance_reply()))

    try:
        result = await assistant_service.chat(
            message=request.message,
            history=[item.model_dump() for item in request.history],
            current_path=request.current_path,
        )
    except RuntimeError as exc:
        # e.g. LLM_API_KEY not configured
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # LLM API errors, network issues, etc.
        raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

    return ResponseModel(data=ChatReply(**result))
