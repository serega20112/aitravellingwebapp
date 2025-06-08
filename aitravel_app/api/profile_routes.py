from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from pydantic import ValidationError

from aitravel_app.services.place_service import PlaceService, UserNotFoundError, PlaceServiceError
from aitravel_app.schemas.place_schemas import LikedPlaceCreateSchema

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/')
@login_required
def user_profile():
    liked_places = []
    recommendation = "Could not fetch recommendations at this time."
    try:
        liked_places = PlaceService.get_liked_places_by_user(current_user.id)
        recommendation = PlaceService.generate_recommendations_for_user(current_user.id)
        
        if "AI service is not configured" in recommendation or            "Could not generate recommendations" in recommendation or            "Content generation was blocked" in recommendation :
            flash("AI recommendations may be affected. Please ensure the Google API key is configured correctly and the AI service is operational.", "warning")
            
    except Exception as e:
        current_app.logger.error(f"Error loading profile for user {current_user.id}: {e}", exc_info=True)
        flash("Could not load all profile data due to an error.", "danger")
        # liked_places и recommendation уже имеют значения по умолчанию
        
    return render_template('profile.html', liked_places=liked_places, recommendation=recommendation)

@bp.route('/like_place', methods=['POST'])
@login_required
def like_place_route():
    try:
        form_data = request.form
        if not all(k in form_data for k in ['city_name', 'latitude', 'longitude']):
            flash("Missing data for liking a place.", 'danger')
            return redirect(request.referrer or url_for('map.index'))

        place_data = LikedPlaceCreateSchema(
            city_name=form_data.get('city_name'),
            latitude=float(form_data.get('latitude')),
            longitude=float(form_data.get('longitude'))
        )
        
        PlaceService.add_liked_place(current_user.id, place_data)
        flash(f"'{place_data.city_name}' added to your liked places!", 'success')
    except ValidationError as e:
        errors = e.errors()
        for error in errors:
            flash(f"Validation Error for liking place ({error['loc'][0]}): {error['msg']}", 'danger')
    except ValueError:
        flash("Invalid latitude or longitude format.", 'danger')
    except UserNotFoundError:
        flash("User not found. Please log in again.", 'danger')
        return redirect(url_for('auth.login'))
    except PlaceServiceError as e:
        flash(f"Could not like place: {str(e)}", 'danger')
    except Exception as e:
        current_app.logger.error(f"Unexpected error liking place for user {current_user.id}: {e}", exc_info=True)
        flash("An unexpected error occurred while liking the place.", 'danger')
    
    return redirect(request.referrer or url_for('profile.user_profile'))
