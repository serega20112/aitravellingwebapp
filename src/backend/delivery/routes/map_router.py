from flask import Blueprint, render_template, request, jsonify, current_app, flash
from pydantic import ValidationError

from src.backend.delivery.shemas.place_shemas import PointInfoRequestSchema

bp = Blueprint("map", __name__)

@bp.route("/")
def index():
    api_key = current_app.config.get("GOOGLE_API_KEY")
    ai_service_configured = api_key and api_key != "YOUR_GOOGLE_API_KEY"
    if not ai_service_configured:
        flash(
            "AI сервис (Google) не настроен. Укажите GOOGLE_API_KEY в .env", "warning"
        )
    flash(ai_service_configured, "success")
    return render_template("index.html", ai_service_configured=ai_service_configured)


@bp.route("/get_location_info", methods=["POST"])
def get_location_info_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Некорректный JSON"}), 400

        point_data = PointInfoRequestSchema(**data)
        place_service = current_app.extensions["services"]["place_service"]
        info = place_service.get_info_for_point(
            point_data.latitude, point_data.longitude
        )

        error_signals = [
            "AI service is not configured",
            "Could not retrieve information",
            "Content generation was blocked",
        ]
        if any(err in info for err in error_signals):
            return jsonify({"error": info}), 503

        return jsonify({"info": info})

    except ValidationError as e:
        current_app.logger.warning(
            f"Ошибка валидации в get_location_info: {e.errors()}"
        )
        return jsonify({"error": "Ошибка валидации", "details": e.errors()}), 400
    except Exception as e:
        current_app.logger.error(
            f"Неожиданная ошибка в get_location_info: {e}", exc_info=True
        )
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500