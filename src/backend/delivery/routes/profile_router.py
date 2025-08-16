from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import login_required, current_user
from pydantic import ValidationError

from src.backend.delivery.shemas.place_shemas import LikedPlaceCreateSchema
from src.backend.domain.exceptions.user_exceptions import UserNotFoundError
from src.backend.domain.exceptions.place_exceptions import PlaceServiceError

bp = Blueprint("profile_router", __name__, url_prefix="/profile")


@bp.route("/")
@login_required
def user_profile():
    liked_places = []
    recommendation = "Не удалось получить рекомендации."
    try:
        profile_use_case = current_app.extensions["services"]["profile_use_case"]
        liked_places = profile_use_case.get_liked_places(current_user.id)
        recommendation = profile_use_case.get_recommendations(current_user.id)

        error_signals = [
            "AI service is not configured",
            "Could not generate recommendations",
            "Content generation was blocked",
        ]
        if any(err in recommendation for err in error_signals):
            flash(
                "Рекомендации ИИ могут быть недоступны. Проверьте наличие HF_TOKEN и работу сервиса ИИ.",
                "warning",
            )

    except Exception as e:
        current_app.logger.error(
            f"Ошибка загрузки профиля пользователя {current_user.id}: {e}",
            exc_info=True,
        )
        flash("Не удалось загрузить все данные профиля из-за ошибки.", "danger")

    return render_template(
        "profile.html", liked_places=liked_places, recommendation=recommendation
    )


@bp.route("/like_place", methods=["POST"])
@login_required
def like_place_route():
    try:
        form_data = request.form
        if not all(k in form_data for k in ["city_name", "latitude", "longitude"]):
            flash("Отсутствуют данные для добавления места.", "danger")
            return redirect(request.referrer or url_for("map.index"))

        place_data = LikedPlaceCreateSchema(
            city_name=form_data.get("city_name"),
            latitude=float(form_data.get("latitude")),
            longitude=float(form_data.get("longitude")),
        )

        profile_use_case = current_app.extensions["services"]["profile_use_case"]
        profile_use_case.add_liked_place(
            current_user.id,
            place_data.city_name,
            place_data.latitude,
            place_data.longitude,
        )
        flash(f"'{place_data.city_name}' добавлен в ваши любимые места!", "success")

    except ValidationError as e:
        for error in e.errors():
            flash(
                f"Ошибка валидации при добавлении места ({error['loc'][0]}): {error['msg']}",
                "danger",
            )
    except ValueError:
        flash("Неверный формат широты или долготы.", "danger")
    except UserNotFoundError:
        flash("Пользователь не найден. Пожалуйста, войдите снова.", "danger")
        return redirect(url_for("auth.login"))
    except PlaceServiceError as e:
        flash(f"Не удалось добавить место: {str(e)}", "danger")
    except Exception as e:
        current_app.logger.error(
            f"Неожиданная ошибка при добавлении места для пользователя {current_user.id}: {e}",
            exc_info=True,
        )
        flash("Произошла непредвиденная ошибка при добавлении места.", "danger")

    return redirect(request.referrer or url_for("profile_router.user_profile"))
