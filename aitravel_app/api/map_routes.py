from flask import Blueprint, render_template, request, jsonify, current_app
from pydantic import ValidationError
from aitravel_app.services.place_service import PlaceService
from aitravel_app.schemas.place_schemas import PointInfoRequestSchema

bp = Blueprint('map', __name__)

@bp.route('/')
def index():
    ai_service_configured = True
    try:
        api_key = current_app.config.get('GOOGLE_API_KEY')
        if not api_key or api_key == "YOUR_GOOGLE_API_KEY_PLACEHOLDER": # Пример плейсхолдера
            ai_service_configured = False
            flash("AI service (Google) is not configured. Please set your Google API key in the .env file.", "warning")
    except Exception:
        ai_service_configured = False
        flash("Error checking AI service configuration.", "danger")

    return render_template('index.html', ai_service_configured=ai_service_configured)

@bp.route('/get_location_info', methods=['POST'])
def get_location_info_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        point_data = PointInfoRequestSchema(**data)
        info = PlaceService.get_info_for_point(point_data.latitude, point_data.longitude)
        
        # Проверяем на специфичные сообщения об ошибках от AI сервиса
        if "AI service is not configured" in info or            "Could not retrieve information" in info or            "Content generation was blocked" in info:
            return jsonify({"error": info}), 503 # Service Unavailable or specific error
            
        return jsonify({"info": info})
    except ValidationError as e:
        current_app.logger.warning(f"Validation error in get_location_info: {e.errors()}")
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_location_info: {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred."}), 500
