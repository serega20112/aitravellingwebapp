import logging
from src.backend.infrastructure.client.init_model.ai_config import MODEL_CONFIG
from src.backend.infrastructure.client.load_model import GPTOSSClient


def get_ai_client(logger: logging.Logger | None = None):
    logger = logger or logging.getLogger(__name__)
    try:
        logger.info(f"Initializing AI client with model: {MODEL_CONFIG['model_path']}")
        return GPTOSSClient()
    except Exception as e:
        logger.error(f"Failed to initialize AI client: {e}", exc_info=True)
        raise RuntimeError(f"AI client initialization failed: {e}")