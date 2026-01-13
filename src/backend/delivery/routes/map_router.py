from flask import Blueprint, current_app, flash, jsonify, render_template, request
from flask.typing import ResponseReturnValue
from flask_login import current_user
from pydantic import ValidationError

from src.backend.delivery.shemas.place_shemas import PointInfoRequestSchema

bp = Blueprint("map", __name__)


@bp.route("/")
def index() -> ResponseReturnValue:
    """
    Отображает главную страницу с интерактивной картой.

    Проверяет конфигурацию ИИ-сервиса и уведомляет пользователя,
    если сервис недоступен или не настроен.

    Returns:
        ResponseReturnValue: HTML-страница карты с флагом доступности ИИ.
    """
    hf_token = current_app.config.get("HF_TOKEN")
    ai_service_configured = bool(hf_token)
    if not ai_service_configured:
        flash("Сервис ИИ не настроен. Укажите HF_TOKEN в .env", "warning")
    return render_template("index.html", ai_service_configured=ai_service_configured)


@bp.route("/get_location_info", methods=["POST"])
def get_location_info_route() -> ResponseReturnValue:
    """
    Возвращает краткое ИИ-описание точки по географическим координатам.

    Принимает координаты точки, валидирует входные данные и
    запрашивает описание у сервиса мест.
    Обрабатывает недоступность или ошибки генерации контента.

    Returns:
        ResponseReturnValue: JSON с описанием точки либо сообщением об ошибке.

    Raises:
        ValidationError: При некорректных координатах запроса.
        Exception: При внутренних ошибках сервиса.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Некорректный JSON"}), 400

        point_data = PointInfoRequestSchema(**data)
        place_service = current_app.extensions["services"]["place_service"]
        info = place_service.get_info_for_point(
            point_data.latitude,
            point_data.longitude,
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


@bp.route("/reverse_geocode", methods=["POST"])
def reverse_geocode_route() -> ResponseReturnValue:
    """
    Выполняет реверс-геокодинг и формирует расширенное описание места.

    Определяет адрес по координатам, извлекает структурированные
    компоненты адреса и при наличии ИИ-сервиса генерирует
    текстовое описание с учётом пользовательских предпочтений.

    Returns:
        ResponseReturnValue: JSON с адресом, компонентами,
        ИИ-описанием и сырыми данными геокодинга.

    Raises:
        ValidationError: При некорректных координатах.
        Exception: При внутренних ошибках обработки.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Некорректный JSON"}), 400

        point = PointInfoRequestSchema(**data)
        services = current_app.extensions["services"]

        geocoder = services.get("geocoding_service")
        if geocoder is None:
            return jsonify({"error": "Сервис геокодинга не сконфигурирован"}), 503

        geo = geocoder.reverse_geocode(
            point.latitude,
            point.longitude,
            lang="ru",
        )
        address = geo.get("display_name")
        addr_components = geo.get("address")

        ai_service = services.get("ai_service")
        ai_text = None
        liked_str = None

        if ai_service is not None:
            try:
                if (
                    hasattr(current_user, "is_authenticated")
                    and current_user.is_authenticated
                ):
                    profile_use_case = services.get("profile_use_case")
                    if profile_use_case:
                        liked = profile_use_case.get_liked_places(current_user.id)
                        if liked:
                            liked_str = ", ".join([p.city_name for p in liked])
            except Exception:
                pass

            if hasattr(ai_service, "get_place_info_with_address_and_prefs"):
                ai_text = ai_service.get_place_info_with_address_and_prefs(
                    address,
                    point.latitude,
                    point.longitude,
                    liked_places_str=liked_str,
                )
            else:
                ai_text = ai_service.get_place_info_with_address(
                    address,
                    point.latitude,
                    point.longitude,
                )

        return jsonify(
            {
                "address": address,
                "address_components": addr_components,
                "ai_description": ai_text,
                "raw": geo.get("raw"),
            }
        )
    except ValidationError as e:
        return jsonify({"error": "Ошибка валидации", "details": e.errors()}), 400
    except Exception as e:
        current_app.logger.error(
            f"Неожиданная ошибка в reverse_geocode: {e}", exc_info=True
        )
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@bp.route("/geocode_query", methods=["POST"])
def ge
