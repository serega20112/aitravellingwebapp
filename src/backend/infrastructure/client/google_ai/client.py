from flask import current_app
from src.backend.infrastructure.client.init_model.ai_config import MODEL_CONFIG
from src.backend.infrastructure.client.load_model import GPTOSSClient


def get_ai_client():
    try:
        current_app.logger.info(f"Initializing AI client with model: {MODEL_CONFIG['model_path']}")
        return GPTOSSClient()
    except Exception as e:
        current_app.logger.error(f"Failed to initialize AI client: {e}", exc_info=True)
        raise RuntimeError(f"AI client initialization failed: {e}")