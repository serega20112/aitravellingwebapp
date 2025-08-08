import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from flask import current_app

from src.backend.infrastructure.client.init_model.ai_config import MODEL_CONFIG


class GPTOSSClient:
    def __init__(self):
        model_path = MODEL_CONFIG.get("model_path")
        if not model_path:
            current_app.logger.error("Model path is not set in MODEL_CONFIG.")
            raise ValueError("MODEL_CONFIG['model_path'] is required.")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        current_app.logger.info(f"Loading GPT-OSS model from {model_path} on {device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path).to(device)
        self.device = device
        current_app.logger.info("GPT-OSS model loaded successfully.")

    def generate(self, prompt: str, **kwargs) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        self.model.generate(
            **inputs,
            max_new_tokens=kwargs.get("max_new_tokens", 256),
            temperature=kwargs
        )
