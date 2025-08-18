"""Схемы запросов/ответов для чата."""

from typing import List, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Сообщение чата в формате роль/текст."""

    role: Literal["user", "assistant", "system"] = Field(
        ..., description="Роль автора сообщения"
    )
    content: str = Field(..., min_length=1, description="Текст сообщения")


class ChatRequest(BaseModel):
    """Запрос на генерацию ответа чата, содержит историю сообщений."""

    session_id: str = Field(..., min_length=1, description="Идентификатор сессии")
    messages: List[ChatMessage] = Field(..., description="История сообщений чата")


class ClearChatRequest(BaseModel):
    """Запрос на очистку истории чата определённой сессии."""

    session_id: str = Field(..., min_length=1)
