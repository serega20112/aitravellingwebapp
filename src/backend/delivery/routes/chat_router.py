"""
Маршруты чата с ИИ для туристической тематики.
"""
from flask import Blueprint, request, jsonify, render_template, current_app
from pydantic import ValidationError

from src.backend.delivery.shemas.chat_shemas import ChatRequest, ClearChatRequest

bp = Blueprint("chat", __name__)


@bp.route("/chat", methods=["GET"])
def chat_page():
    """Возвращает страницу веб-чата с ИИ."""
    return render_template("chat.html")


@bp.route("/api/chat", methods=["POST"])
def chat_api():
    """Обрабатывает запрос чата, валидирует вход и возвращает ответ ассистента."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Некорректный JSON"}), 400
        req = ChatRequest(**data)
        repo = current_app.extensions["services"]["chat_repo"]
        ai = current_app.extensions["services"]["ai_service"]
        history = repo.get(req.session_id)
        for m in req.messages:
            history.append({"role": m.role, "content": m.content})
        answer = ai.chat(history)
        repo.append(req.session_id, "assistant", answer)
        return jsonify({"answer": answer})
    except ValidationError as e:
        return jsonify({"error": "Ошибка валидации", "details": e.errors()}), 400
    except Exception as e:
        current_app.logger.error(f"Ошибка API чата: {e}", exc_info=True)
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@bp.route("/api/chat/clear", methods=["POST"])
def chat_clear():
    """Очищает историю сообщений указанной сессии."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Некорректный JSON"}), 400
        req = ClearChatRequest(**data)
        repo = current_app.extensions["services"]["chat_repo"]
        repo.clear(req.session_id)
        return jsonify({"status": "ok"})
    except ValidationError as e:
        return jsonify({"error": "Ошибка валидации", "details": e.errors()}), 400
    except Exception as e:
        current_app.logger.error(f"Ошибка очистки чата: {e}", exc_info=True)
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500
