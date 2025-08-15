"""
Клиент Hugging Face Inference API.
Инкапсулирует инициализацию клиента на основе настроек приложения.
"""
from typing import Optional
from huggingface_hub import InferenceClient
from flask import current_app


def get_hf_client() -> InferenceClient:
    """Возвращает инициализированный InferenceClient из конфигурации Flask."""
    cfg = current_app.config
    token: Optional[str] = cfg.get("HF_TOKEN")
    provider: str = cfg.get("HF_PROVIDER", "fireworks-ai")
    if not token:
        raise RuntimeError("HF_TOKEN отсутствует в конфигурации приложения")
    return InferenceClient(provider=provider, api_key=token)
