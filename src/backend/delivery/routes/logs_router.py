from __future__ import annotations
from flask import Blueprint, render_template, request, jsonify, current_app, abort
from flask_login import login_required
from werkzeug.exceptions import BadRequest

bp = Blueprint("logs", __name__, url_prefix="/logs")


@bp.before_request
def _restrict_logs():
    # Доступ только если явно включено в конфиге (для разработчиков)
    if not current_app.config.get("SHOW_LOGS_LINK", False):
        abort(404)


@bp.route("/", methods=["GET"])  # UI
@login_required
def logs_ui():
    return render_template("logs.html")


@bp.route("/api/search", methods=["GET"])  # API
@login_required
def logs_search_api():
    query = request.args.get("q")
    level = request.args.get("level")
    from_ts = request.args.get("from")
    to_ts = request.args.get("to")
    try:
        size = int(request.args.get("size", "50"))
        page = int(request.args.get("page", "0"))
    except ValueError as ex:  # pragma: no cover
        raise BadRequest("Invalid pagination params") from ex

    log_service = current_app.extensions.get("services", {}).get("log_service")
    if log_service is None or not getattr(log_service, "enabled", False):
        return jsonify({"total": 0, "hits": [], "note": "Elasticsearch недоступен или не настроен"})

    data = log_service.search_logs(
        query=query, level=level, from_ts=from_ts, to_ts=to_ts, size=size, page=page
    )
    return jsonify(data)
