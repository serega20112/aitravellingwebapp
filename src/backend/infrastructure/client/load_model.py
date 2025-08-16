import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.backend.infrastructure.client.init_model.ai_config import MODEL_CONFIG


class GPTOSSClient:
    def __init__(self, logger: logging.Logger | None = None):
        self._logger = logger or logging.getLogger(__name__)
        model_path = MODEL_CONFIG.get("model_path")
        if not model_path:
            self._logger.error("Model path is not set in MODEL_CONFIG.")
            raise ValueError("MODEL_CONFIG['model_path'] is required.")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        self._logger.info(f"Loading GPT-OSS model from {model_path} on {device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path).to(device)
        self.device = device
        self._logger.info("GPT-OSS model loaded successfully.")

    def generate(self, prompt: str, **kwargs) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=kwargs.get("max_new_tokens", 256),
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.95),
            do_sample=kwargs.get("do_sample", True),
            early_stopping=kwargs.get("early_stopping", True),
        )
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Если prompt включён в начале ответа, уберём его
        return text[len(prompt):].strip() if text.startswith(prompt) else text.strip()
