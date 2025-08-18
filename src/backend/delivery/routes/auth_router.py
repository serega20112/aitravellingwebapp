"""Маршруты аутентификации пользователей (регистрация/вход/выход)."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required, login_user, logout_user
from pydantic import ValidationError

from src.backend.delivery.shemas.user_shemas import UserCreateSchema
from src.backend.domain.exceptions.user_exceptions import (
    InvalidCredentials,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.backend.services.user.user_service import UserService

auth_router = Blueprint("auth_router", __name__, url_prefix="/auth")
user_service = UserService()  # Используем UserService вместо UserUseCase


@auth_router.route("/register", methods=["GET", "POST"])
def register() -> ResponseReturnValue:
    """Страница регистрации и обработка отправленной формы."""
    if current_user.is_authenticated:
        return redirect(url_for("map.index"))

    if request.method == "POST":
        try:
            form_data = UserCreateSchema(**request.form)
            user_service.register_user(form_data.username, form_data.password)
            flash("Регистрация прошла успешно. Войдите в систему.", "success")
            return redirect(url_for("auth_router.login"))
        except ValidationError as e:
            for error in e.errors():
                flash(
                    f"Ошибка валидации: поле {error['loc'][0]} — {error['msg']}",
                    "danger",
                )
        except UserAlreadyExistsError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash("Произошла ошибка. Попробуйте позже.", "danger")
            print(e)

    return render_template("register.html")


@auth_router.route("/login", methods=["GET", "POST"])
def login() -> ResponseReturnValue:
    """Страница входа и обработка логина пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for("map.index"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if not username or not password:
            flash("Логин и пароль обязательны", "danger")
            return render_template("login.html"), 400

        try:
            user = user_service.authenticate_user(username, password)
            login_user(user, remember=request.form.get("remember") == "on")
            flash("Вы успешно вошли в систему", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("map.index"))
        except (UserNotFoundError, InvalidCredentials) as e:
            flash(str(e), "danger")
        except Exception as e:
            flash("Произошла ошибка при входе", "danger")
            print(e)

    return render_template("login.html")


@auth_router.route("/logout")
@login_required
def logout() -> ResponseReturnValue:
    """Выйти из аккаунта и перенаправить на страницу входа."""
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("auth_router.login"))
