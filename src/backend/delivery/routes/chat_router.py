from flask import Blueprint, current_app, jsonify, render_template, request
from flask.typing import ResponseReturnValue
from flask_login import current_user
from pydantic import ValidationError

from src.backend.delivery.shemas.chat_shemas import ChatRequest, ClearChatRequest

bp = Blueprint("chat", __name__)


@bp.route("/chat", methods=["GET"])
def chat_page() -> ResponseReturnValue:
    """
    Отображает страницу веб-чата с ИИ-ассистентом.

    Используется для инициализации пользовательского интерфейса чата
    и не содержит серверной логики обработки сообщений.

    Returns:
        ResponseReturnValue: HTML-страница веб-чата.
    """
    return render_template("chat.html")


@bp.route("/api/chat", methods=["POST"])
def chat_api() -> ResponseReturnValue:
    """
    Обрабатывает API-запрос диалога с ИИ-ассистентом.

    Валидирует входные данные запроса, восстанавливает историю диалога
    по идентификатору сессии и передаёт сообщения в ИИ-сервис.
    При наличии аутентифицированного пользователя обогащает контекст
    предпочтениями понравившихся туристических мест.

    Returns:
        ResponseReturnValue: JSON-ответ с сообщением ассистента
        или описанием ошибки.

    Raises:
        ValidationError: При некорректных данных запроса.
        Exception: При внутренних ошибках обработки чата.
    """
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

        payload_history = list(history)

        try:
            if (
                hasattr(current_user, "is_authenticated")
                and current_user.is_authenticated
            ):
                profile_use_case = current_app.extensions["services"][
                    "profile_use_case"
                ]
                liked_places = profile_use_case.get_liked_places(current_user.id)
                if liked_places:
                    liked_str = ", ".join([p.city_name for p in liked_places])
                    system_context = (
                        "Контекст пользователя: ему нравятся следующие места: "
                        + liked_str
                        + ". Если пользователь просит рекомендации, опирайся на эти предпочтения. "
                        "Если он уточняет новое направление, подстрой рекомендации под это пожелание, "
                        "сохраняя логику его предыдущих предпочтений. Отвечай по-русски, кратко и по делу."
                    )
                    payload_history = [
                        {"role": "system", "content": system_context}
                    ] + payload_history
        except Exception:
            pass

        answer = ai.chat(payload_history)
        repo.append(req.session_id, "assistant", answer)

        return jsonify({"answer": answer})
    except ValidationError as e:
        return jsonify(
            {"error": "Ошибка валидации", "details": e.errors()}), 400
    except Exception as e:
        current_app.logger.error(f"Ошибка API чата: {e}", exc_info=True)
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@bp.route("/api/chat/clear", methods=["POST"])
def chat_clear() -> ResponseReturnValue:
    """
    Очищает историю диалога для указанной сессии чата.

    Используется для сброса состояния чата и начала нового диалога
    в рамках той же пользовательской сессии.

    Returns:
        ResponseReturnValue: JSON-ответ со статусом выполнения операции.

    Raises:
        ValidationError: При некорректных данных запроса.
        Exception: При внутренних ошибках очистки истории.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Некорректный JSON"}), 400

        req = ClearChatRequest(**data)
        repo = current_app.extensions["services"]["chat_repo"]
        repo.clear(req.session_id)

        return jsonify({"status": "ok"})
    except ValidationError as e:
        return jsonify(
            {"error": "Ошибка валидации", "details": e.errors()}), 400
    except Exception as e:
        current_app.logger.error(f"Ошибка очистки чата: {e}", exc_info=True)
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500
