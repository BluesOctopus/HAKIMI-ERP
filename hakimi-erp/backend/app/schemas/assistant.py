from typing import List, Optional

from pydantic import BaseModel, Field


class ChatHistoryItem(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)


class PendingAction(BaseModel):
    """A planned but not yet executed demo action, awaiting user confirmation.

    ``qty`` is a decimal encoded as string to avoid float rounding.
    """

    intent: str
    so_id: Optional[str] = None
    qty: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: List[ChatHistoryItem] = Field(default_factory=list)
    current_path: Optional[str] = None
    pending_action: Optional[PendingAction] = None


class NavigationTarget(BaseModel):
    label: str
    route: str


class ChatStep(BaseModel):
    """One scripted execution step shown by the demo assistant."""

    icon: str
    text: str


class ChatReply(BaseModel):
    reply: str
    navigation: Optional[NavigationTarget] = None
    suggestions: List[str] = Field(default_factory=list)
    steps: List[ChatStep] = Field(default_factory=list)
    pending_action: Optional[PendingAction] = None
