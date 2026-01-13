from __future__ import annotations

from flask import Blueprint, abort, current_app, jsonify, render_template, request
from flask.typing import ResponseReturnValue
from flask_login import login_required
from werkzeug.exceptions import BadRequest

bp = Blueprint("logs", __name__, url_prefix="/logs")


@bp.before_request
def _restrict_logs() -> None:
    """
    Ограничивает доступ к маршрутам логов на уровне запроса.

    Проверяет конфигурацию приложения и запрещает доступ
    к просмотру и поиску логов, если функциональность
    не разрешена явно для текущего окружения.

    Raises:
        HTTPException: Возвращает 404, если доступ к логам отключён.
    """
    if not current_app.config.get("SHOW_LOGS_LINK", False):
        abort(404)


@bp.route("/", methods=["GET"])
@login_required
def logs_ui() -> ResponseReturnValue:
    """
    Отображает пользовательский интерфейс просмотра логов.

    Предназначен для разработчиков и используется
    для визуального анализа логов приложения.

    Returns:
        ResponseReturnValue: HTML-страница интерфейса логов.
    """
    return render_template("logs.html")


@bp.route("/api/search", methods=["GET"])
@login_required
def logs_search_api() -> ResponseReturnValue:
    """
    Выполняет поиск логов по параметрам запроса и возвращает результат.

    Поддерживает фильтрацию по текстовому запросу, уровню логирования
    и временному диапазону, а также постраничную навигацию.
    Используется исключительно в среде разработки.

    Returns:
        ResponseReturnValue: JSON-ответ с найденными логами и метаданными.

    Raises:
        BadRequest: При некорректных параметрах пагинации.
        Exception: При внутренних ошибках сервиса логов.
    """
    query = request.args.get("q")
    level = request.args.get("level")
    from_ts = request.args.get("from")
    to_ts = request.args.get("to")

    try:
        size = int(request.args.get("size", "50"))
        page = int(request.args.get("page", "0"))
    except ValueError as ex:
        raise BadRequest("Invalid pagination params") from ex

    log_service = current_app.extensions.get("services", {}).get("log_service")
    if log_service is None or not getattr(log_service, "enabled", False):
        return jsonify(
            {
                "total": 0,
                "hits": [],
                "note": "Elasticsearch недоступен или не настроен",
            }
        )

    data = log_service.search_logs(
        query=query,
        level=level,
        from_ts=from_ts,
        to_ts=to_ts,
        size=size,
        page=page,
    )
    return jsonify(data)
