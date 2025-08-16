"""
Маршруты чата с ИИ для туристической тематики.
"""
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import current_user
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
        # Добавляем контекст с понравившимися местами, если пользователь аутентифицирован
        payload_history = list(history)
        try:
            if hasattr(current_user, "is_authenticated") and current_user.is_authenticated:
                profile_use_case = current_app.extensions["services"]["profile_use_case"]
                liked_places = profile_use_case.get_liked_places(current_user.id)
                if liked_places:
                    liked_str = ", ".join([p.city_name for p in liked_places])
                    system_context = (
                        "Контекст пользователя: ему нравятся следующие места: "
                        + liked_str
                        + ". Если пользователь просит рекомендации, опирайся на эти предпочтения. "
                        "Если он уточняет новое направление (например, 'хочу в Сибирь'), подстрой рекомендации под это пожелание, "
                        "сохраняя логику его предыдущих предпочтений. Отвечай по-русски, кратко и по делу."
                    )
                    payload_history = [{"role": "system", "content": system_context}] + payload_history
        except Exception as _:
            # Не ломаем чат, если не удалось подгрузить понравившиеся места
            pass

        answer = ai.chat(payload_history)
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
