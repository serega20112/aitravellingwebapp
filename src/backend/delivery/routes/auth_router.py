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
user_service = UserService()


@auth_router.route("/register", methods=["GET", "POST"])
def register() -> ResponseReturnValue:
    """Обрабатывает страницу регистрации пользователя и отправку формы.

    При GET-запросе отображает страницу регистрации.
    При POST-запросе валидирует данные формы, создаёт нового пользователя
    и перенаправляет на страницу входа при успешной регистрации.

    Returns:
        ResponseReturnValue: HTML-страница регистрации или HTTP-редирект.

    Raises:
        ValidationError: При ошибках валидации данных формы.
        UserAlreadyExistsError: Если пользователь с таким именем уже существует.
        Exception: При любой непредвиденной ошибке во время регистрации.
    """
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
    """Обрабатывает страницу входа и аутентификацию пользователя.

    При GET-запросе отображает страницу входа.
    При POST-запросе валидирует входные данные, аутентифицирует пользователя
    и выполняет вход с учетом опции "запомнить".

    Returns:
        ResponseReturnValue: HTML-страница входа или HTTP-редирект.

    Raises:
        UserNotFoundError: Если пользователь не найден.
        InvalidCredentials: При неверном пароле.
        Exception: При любой непредвиденной ошибке во время входа.
    """
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
    """Выполняет выход пользователя и перенаправление на страницу входа.

    Returns:
        ResponseReturnValue: HTTP-редирект на страницу входа.
    """
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("auth_router.login"))
