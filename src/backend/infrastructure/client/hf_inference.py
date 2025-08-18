"""
Клиент Hugging Face Inference API.

Инкапсулирует инициализацию клиента на основе переданной конфигурации.
"""

from typing import Optional

from huggingface_hub import InferenceClient


def create_hf_client(config: dict) -> InferenceClient:
    """Создаёт InferenceClient на основе явной конфигурации.

    Ожидаемые ключи:
    - HF_TOKEN (str, обязательно)
    - HF_PROVIDER (str, по умолчанию "fireworks-ai")
    """
    token: Optional[str] = config.get("HF_TOKEN")
    provider: str = config.get("HF_PROVIDER", "fireworks-ai")
    if not token:
        raise RuntimeError("HF_TOKEN отсутствует в конфигурации приложения")
    return InferenceClient(provider=provider, api_key=token)
