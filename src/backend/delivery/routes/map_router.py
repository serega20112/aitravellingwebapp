from flask import Blueprint, render_template, request, jsonify, current_app, flash
from flask_login import current_user
from pydantic import ValidationError

from src.backend.delivery.shemas.place_shemas import PointInfoRequestSchema

bp = Blueprint("map", __name__)

@bp.route("/")
def index():
    """
    Главная страница с картой. Проверяется настройка ИИ‑сервиса по токену
    Hugging Face (HF_TOKEN) в конфигурации приложения.
    """
    hf_token = current_app.config.get("HF_TOKEN")
    ai_service_configured = bool(hf_token)
    if not ai_service_configured:
        flash("Сервис ИИ не настроен. Укажите HF_TOKEN в .env", "warning")
    return render_template("index.html", ai_service_configured=ai_service_configured)


@bp.route("/get_location_info", methods=["POST"])
def get_location_info_route():
    """
    Возвращает краткое описание точки по координатам.

    Тело запроса: {"latitude": float, "longitude": float}
    Ответ: {"info": str} либо {"error": str}
    """
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


@bp.route("/reverse_geocode", methods=["POST"])
def reverse_geocode_route():
    """
    Реверс‑геокодинг с ИИ‑описанием.

    Тело запроса: {"latitude": float, "longitude": float}
    Ответ: {
        "address": str | null,
        "address_components": dict | null,
        "ai_description": str | null,
        "raw": dict | null,
        "error": str | null
    }
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

        geo = geocoder.reverse_geocode(point.latitude, point.longitude, lang="ru")
        address = geo.get("display_name")
        addr_components = geo.get("address")

        ai_service = services.get("ai_service")
        ai_text = None
        if ai_service is not None:
            liked_str = None
            try:
                if hasattr(current_user, "is_authenticated") and current_user.is_authenticated:
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
        return (
            jsonify({"error": "Ошибка валидации", "details": e.errors()}),
            400,
        )
    except Exception as e:
        current_app.logger.error(
            f"Неожиданная ошибка в reverse_geocode: {e}", exc_info=True
        )
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@bp.route("/geocode_query", methods=["POST"])
def geocode_query_route():
    """
    Поиск по текстовому запросу с нормализацией через ИИ и описанием места.

    Тело: {"query": str}
    Ответ: {
        "query": str,
        "normalized_query": str | null,
        "address": str | null,
        "lat": float | null,
        "lon": float | null,
        "ai_description": str | null,
        "raw": dict | null,
        "error": str | null
    }
    """
    try:
        data = request.get_json()
        if not data or not isinstance(data.get("query"), str):
            return jsonify({"error": "Некорректный JSON или отсутствует query"}), 400

        query = data["query"].strip()
        services = current_app.extensions["services"]
        geocoder = services.get("geocoding_service")
        ai_service = services.get("ai_service")
        if geocoder is None or ai_service is None:
            return jsonify({"error": "Сервисы геокодинга или ИИ не сконфигурированы"}), 503

        normalized = None
        try:
            if hasattr(ai_service, "normalize_location_query"):
                normalized = ai_service.normalize_location_query(query)
        except Exception:
            normalized = None

        search_q = normalized or query

        geo = geocoder.search(search_q, lang="ru", limit=1)
        address = geo.get("display_name")
        lat = geo.get("lat")
        lon = geo.get("lon")

        liked_str = None
        try:
            if hasattr(current_user, "is_authenticated") and current_user.is_authenticated:
                profile_use_case = services.get("profile_use_case")
                if profile_use_case:
                    liked = profile_use_case.get_liked_places(current_user.id)
                    if liked:
                        liked_str = ", ".join([p.city_name for p in liked])
        except Exception:
            pass

        ai_text = None
        if lat is not None and lon is not None:
            if hasattr(ai_service, "get_place_info_with_address_and_prefs"):
                ai_text = ai_service.get_place_info_with_address_and_prefs(
                    address,
                    lat,
                    lon,
                    liked_places_str=liked_str,
                )
            else:
                ai_text = ai_service.get_place_info_with_address(address, lat, lon)

        return jsonify(
            {
                "query": query,
                "normalized_query": normalized,
                "address": address,
                "lat": lat,
                "lon": lon,
                "ai_description": ai_text,
                "raw": geo.get("raw"),
            }
        )
    except Exception as e:
        current_app.logger.error(
            f"Неожиданная ошибка в geocode_query: {e}", exc_info=True
        )
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500