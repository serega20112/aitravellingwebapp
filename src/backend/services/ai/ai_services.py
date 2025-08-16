import logging
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from src.backend.infrastructure.client.init_model.ai_config import MODEL_CONFIG


class AIService:
    def __init__(self, logger: logging.Logger | None = None):
        self._logger = logger or logging.getLogger(__name__)
        model_path = MODEL_CONFIG["model_path"]
        self.device = "cuda" if torch.cuda.is_available() else "cuda"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path).to(self.device)
        self.temperature = MODEL_CONFIG.get("temperature", 0.7)
        self.top_p = MODEL_CONFIG.get("top_p", 0.95)
        self.do_sample = MODEL_CONFIG.get("do_sample", True)
        self.max_new_tokens = MODEL_CONFIG.get("max_new_tokens", 100)

    def _generate(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                do_sample=self.do_sample,
                early_stopping=MODEL_CONFIG.get("early_stopping", True),
            )
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text[len(prompt):].strip()  # убрать prompt из начала

    def get_place_info(self, latitude: float, longitude: float) -> str:
        prompt = (
            f"Ты — полезный туристический ассистент. Предоставь краткую и интересную информацию "
            f"о месте с координатами широта {latitude}, долгота {longitude}. "
            f"Не больше 100 слов. Пиши на русском языке."
        )
        try:
            response_text = self._generate(prompt)
            if not response_text:
                self._logger.warning("Пустой ответ от модели на get_place_info.")
                return "Не удалось получить информацию: пустой ответ модели."
            return response_text
        except Exception as e:
            self._logger.error(f"Ошибка генерации get_place_info: {e}", exc_info=True)
            return f"Ошибка сервиса ИИ: {str(e)}"

    def get_travel_recommendation(self, liked_places_str: str) -> str:
        prompt = (
            f"Ты — эксперт по рекомендациям путешествий. На основе списка понравившихся мест: {liked_places_str}. "
            f"Порекомендуй новое место для путешествия и кратко объясни почему (около 100-150 слов). "
            f"Пиши на русском языке."
        )
        try:
            response_text = self._generate(prompt)
            if not response_text:
                self._logger.warning("Пустой ответ от модели на get_travel_recommendation.")
                return "Не удалось получить рекомендации: пустой ответ модели."
            return response_text
        except Exception as e:
            self._logger.error(f"Ошибка генерации get_travel_recommendation: {e}", exc_info=True)
            return f"Ошибка сервиса ИИ: {str(e)}"
