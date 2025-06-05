import os
import stat

def create_project_structure():
    project_name = "aitravel_app"
    base_dir = project_name

    dirs = [
        base_dir,
        os.path.join(base_dir, "aitravel_app"),
        os.path.join(base_dir, "aitravel_app", "api"),
        os.path.join(base_dir, "aitravel_app", "models"),
        os.path.join(base_dir, "aitravel_app", "schemas"),
        os.path.join(base_dir, "aitravel_app", "services"),
        os.path.join(base_dir, "aitravel_app", "ai"),
        os.path.join(base_dir, "aitravel_app", "core"),
        os.path.join(base_dir, "aitravel_app", "config"),
        os.path.join(base_dir, "aitravel_app", "templates"),
        os.path.join(base_dir, "aitravel_app", "static"),
        os.path.join(base_dir, "aitravel_app", "static", "css"),
        os.path.join(base_dir, "aitravel_app", "static", "js"),
        os.path.join(base_dir, "migrations"),
        os.path.join(base_dir, "instance")
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)

    files = {
        os.path.join(base_dir, ".env"): """\
GOOGLE_API_KEY="AIzaSyAl_NXx0Q5BHLzi0pXSIaReDR6K2Rf1Rjc"
SECRET_KEY="super_secret_key_ai_app"
# OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE" # Теперь не используется

# База данных будет создана в корневой папке проекта как aitravel.db
SQLALCHEMY_DATABASE_URI="sqlite:///../aitravel.db"
""",
        os.path.join(base_dir, "requirements.txt"): """\
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.30
Flask-Migrate==4.0.7
python-dotenv==1.0.1
google-generativeai==0.7.0 # Замена для OpenAI
werkzeug==3.0.3
Flask-Login==0.6.3
pydantic==2.7.4
email-validator==2.2.0
psycopg2-binary # Пример, если используется PostgreSQL
# mysql-connector-python # Пример, если используется MySQL
""",
        os.path.join(base_dir, "run.py"): """\
import os
from aitravel_app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
""",
        os.path.join(base_dir, "aitravel_app", "__init__.py"): """\
from flask import Flask
from flask_login import LoginManager
from .config.config import DevelopmentConfig
from .core.db import db
from .core.migrate import migrate
from .models.user import User
import os

def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=True)

    if config_class is None:
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(config_class)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        from .api import auth_routes, map_routes, profile_routes
        app.register_blueprint(auth_routes.bp)
        app.register_blueprint(map_routes.bp)
        app.register_blueprint(profile_routes.bp)

    return app
""",
        os.path.join(base_dir, "aitravel_app", "config", "__init__.py"): "",
        os.path.join(base_dir, "aitravel_app", "config", "config.py"): """\
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    # OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') # Больше не используется

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///aitravel_dev.db'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI_TEST') or 'sqlite:///aitravel_test.db'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
""",
        os.path.join(base_dir, "aitravel_app", "core", "__init__.py"): "",
        os.path.join(base_dir, "aitravel_app", "core", "db.py"): """\
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
""",
        os.path.join(base_dir, "aitravel_app", "core", "migrate.py"): """\
from flask_migrate import Migrate

migrate = Migrate()
""",
        os.path.join(base_dir, "aitravel_app", "core", "security.py"): """\
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    return generate_password_hash(password)

def verify_password(stored_password_hash, provided_password):
    return check_password_hash(stored_password_hash, provided_password)
""",
        os.path.join(base_dir, "aitravel_app", "models", "__init__.py"): """\
from .user import User
from .liked_place import LikedPlace

__all__ = ['User', 'LikedPlace']
""",
        os.path.join(base_dir, "aitravel_app", "models", "user.py"): """\
from aitravel_app.core.db import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    liked_places = db.relationship('LikedPlace', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'
""",
        os.path.join(base_dir, "aitravel_app", "models", "liked_place.py"): """\
from aitravel_app.core.db import db

class LikedPlace(db.Model):
    __tablename__ = 'liked_places'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<LikedPlace {self.city_name} by User ID {self.user_id}>'
""",
        os.path.join(base_dir, "aitravel_app", "schemas", "__init__.py"): """\
from .user_schemas import UserCreateSchema, UserResponseSchema
from .place_schemas import LikedPlaceCreateSchema, LikedPlaceResponseSchema, PointInfoRequestSchema

__all__ = [
    'UserCreateSchema', 'UserResponseSchema',
    'LikedPlaceCreateSchema', 'LikedPlaceResponseSchema', 'PointInfoRequestSchema'
]
""",
        os.path.join(base_dir, "aitravel_app", "schemas", "user_schemas.py"): """\
from pydantic import BaseModel, constr

class UserCreateSchema(BaseModel):
    username: constr(min_length=3, max_length=80)
    password: constr(min_length=6)

class UserResponseSchema(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
""",
        os.path.join(base_dir, "aitravel_app", "schemas", "place_schemas.py"): """\
from pydantic import BaseModel, constr

class PointInfoRequestSchema(BaseModel):
    latitude: float
    longitude: float

class LikedPlaceCreateSchema(BaseModel):
    city_name: constr(min_length=1, max_length=100)
    latitude: float
    longitude: float

class LikedPlaceResponseSchema(BaseModel):
    id: int
    user_id: int
    city_name: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
""",
        os.path.join(base_dir, "aitravel_app", "ai", "__init__.py"): "",
        os.path.join(base_dir, "aitravel_app", "ai", "client.py"): """\
import google.generativeai as genai
from flask import current_app

def get_google_ai_model():
    api_key = current_app.config.get('GOOGLE_API_KEY')
    if not api_key or api_key == "YOUR_GOOGLE_API_KEY_PLACEHOLDER": # Пример плейсхолдера
        current_app.logger.error("Google API key is not configured or is a placeholder.")
        raise ValueError("GOOGLE_API_KEY not configured or is a placeholder. Please set it in your .env file.")
    
    try:
        genai.configure(api_key=api_key)
        # Вы можете выбрать конкретную модель здесь, если это необходимо,
        # или передать имя модели в сервисные функции.
        # Например, model = genai.GenerativeModel('gemini-pro')
        # Для простоты, пока возвращаем сконфигурированный модуль genai.
        # Сервисы будут вызывать genai.GenerativeModel() сами.
        return genai # Возвращаем сконфигурированный модуль
    except Exception as e:
        current_app.logger.error(f"Failed to configure Google AI SDK: {e}")
        raise ValueError(f"Failed to configure Google AI SDK: {e}")

""",
        os.path.join(base_dir, "aitravel_app", "ai", "services.py"): """\
from .client import get_google_ai_model
from flask import current_app

# Рекомендуется использовать более новые модели, если доступны, например 'gemini-1.5-flash'
# 'gemini-pro' - более старая, но все еще рабочая модель
DEFAULT_GOOGLE_MODEL_NAME = 'gemini-1.5-flash-latest'


def get_place_info_from_ai(latitude: float, longitude: float) -> str:
    try:
        genai_configured_module = get_google_ai_model() # Получаем сконфигурированный модуль
        model = genai_configured_module.GenerativeModel(DEFAULT_GOOGLE_MODEL_NAME)
        
        prompt = f"You are a helpful travel assistant. Provide concise and interesting information about the location at latitude {latitude}, longitude {longitude}. Keep it under 100 words."
        
        response = model.generate_content(prompt)
        
        # Проверка на наличие блокировок или ошибок в ответе
        if not response.candidates or not response.candidates[0].content.parts:
             if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = response.prompt_feedback.block_reason
                current_app.logger.warning(f"Google AI content generation blocked for place info. Reason: {block_reason}")
                return f"Could not retrieve information: Content generation was blocked (Reason: {block_reason}). Please try a different query or location."
             current_app.logger.warning("Google AI returned an empty response for place info.")
             return "Could not retrieve information: AI returned an empty response."

        return response.text.strip()
    except ValueError as ve: # Ошибка конфигурации ключа
        current_app.logger.error(f"AI Service (Google) Configuration Error: {ve}")
        return "AI service is not configured. Please check API key."
    except Exception as e:
        current_app.logger.error(f"Google AI API error for place info: {e}", exc_info=True)
        # Попытка извлечь более детальную информацию об ошибке, если это google.api_core.exceptions
        error_message = str(e)
        if hasattr(e, 'message'): # Для некоторых ошибок Google
            error_message = e.message
        return f"Could not retrieve information at this time due to an AI service error: {error_message}"

def get_travel_recommendation_from_ai(liked_places_str: str) -> str:
    try:
        genai_configured_module = get_google_ai_model() # Получаем сконфигурированный модуль
        model = genai_configured_module.GenerativeModel(DEFAULT_GOOGLE_MODEL_NAME)
        
        prompt = f"You are a travel recommendation expert. Based on the list of liked places: {liked_places_str}. Can you recommend a new travel destination for me and briefly explain why (around 100-150 words)?"
        
        response = model.generate_content(prompt)

        if not response.candidates or not response.candidates[0].content.parts:
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = response.prompt_feedback.block_reason
                current_app.logger.warning(f"Google AI content generation blocked for recommendations. Reason: {block_reason}")
                return f"Could not generate recommendations: Content generation was blocked (Reason: {block_reason}). Please try adjusting your liked places."
            current_app.logger.warning("Google AI returned an empty response for recommendations.")
            return "Could not generate recommendations: AI returned an empty response."

        return response.text.strip()
    except ValueError as ve: # Ошибка конфигурации ключа
        current_app.logger.error(f"AI Service (Google) Configuration Error: {ve}")
        return "AI service is not configured. Please check API key."
    except Exception as e:
        current_app.logger.error(f"Google AI API error for recommendation: {e}", exc_info=True)
        error_message = str(e)
        if hasattr(e, 'message'):
            error_message = e.message
        return f"Could not generate recommendations at this time due to an AI service error: {error_message}"
""",
        os.path.join(base_dir, "aitravel_app", "services", "__init__.py"): "",
        os.path.join(base_dir, "aitravel_app", "services", "user_service.py"): """\
from aitravel_app.models import User
from aitravel_app.core.db import db
from aitravel_app.core.security import hash_password, verify_password
from aitravel_app.schemas.user_schemas import UserCreateSchema
from sqlalchemy.exc import IntegrityError

class UserServiceError(Exception):
    pass

class UserAlreadyExistsError(UserServiceError):
    pass

class UserService:
    @staticmethod
    def create_user(user_data: UserCreateSchema) -> User:
        if User.query.filter_by(username=user_data.username).first():
            raise UserAlreadyExistsError("Username already exists")

        hashed_pw = hash_password(user_data.password)
        new_user = User(username=user_data.username, password_hash=hashed_pw)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise UserAlreadyExistsError("Username already exists (database integrity error)")
        except Exception as e:
            db.session.rollback()
            raise UserServiceError(f"Could not create user: {e}")
        return new_user

    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        return User.query.get(user_id)

    @staticmethod
    def check_user_credentials(username: str, password_plaintext: str) -> User | None:
        user = UserService.get_user_by_username(username)
        if user and verify_password(user.password_hash, password_plaintext):
            return user
        return None
""",
        os.path.join(base_dir, "aitravel_app", "services", "place_service.py"): """\
from aitravel_app.models import LikedPlace, User
from aitravel_app.core.db import db
from aitravel_app.ai.services import get_place_info_from_ai, get_travel_recommendation_from_ai
from aitravel_app.schemas.place_schemas import LikedPlaceCreateSchema
from flask import current_app

class PlaceServiceError(Exception):
    pass

class UserNotFoundError(PlaceServiceError):
    pass

class PlaceService:
    @staticmethod
    def get_info_for_point(latitude: float, longitude: float) -> str:
        return get_place_info_from_ai(latitude, longitude)

    @staticmethod
    def add_liked_place(user_id: int, place_data: LikedPlaceCreateSchema) -> LikedPlace:
        user = User.query.get(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        existing_liked_place = LikedPlace.query.filter_by(
            user_id=user_id,
            latitude=place_data.latitude,
            longitude=place_data.longitude
        ).first()

        if existing_liked_place:
            current_app.logger.info(f"Place {place_data.city_name} at {place_data.latitude},{place_data.longitude} already liked by user {user_id}.")
            return existing_liked_place

        new_liked_place = LikedPlace(
            user_id=user_id,
            city_name=place_data.city_name,
            latitude=place_data.latitude,
            longitude=place_data.longitude
        )
        db.session.add(new_liked_place)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding liked place: {e}")
            raise PlaceServiceError(f"Could not add liked place: {e}")
        return new_liked_place

    @staticmethod
    def get_liked_places_by_user(user_id: int) -> list[LikedPlace]:
        return LikedPlace.query.filter_by(user_id=user_id).order_by(LikedPlace.id.desc()).all()

    @staticmethod
    def generate_recommendations_for_user(user_id: int) -> str:
        liked_places = PlaceService.get_liked_places_by_user(user_id)
        if not liked_places:
            return "Not enough liked places to generate recommendations. Please like some places first!"

        liked_places_names = [place.city_name for place in liked_places]
        liked_places_str = ", ".join(liked_places_names)

        return get_travel_recommendation_from_ai(liked_places_str)
""",
        os.path.join(base_dir, "aitravel_app", "api", "__init__.py"): "",
        os.path.join(base_dir, "aitravel_app", "api", "auth_routes.py"): """\
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from pydantic import ValidationError

from aitravel_app.services.user_service import UserService, UserAlreadyExistsError
from aitravel_app.schemas.user_schemas import UserCreateSchema

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('map.index'))
    if request.method == 'POST':
        try:
            form_data = request.form
            if not form_data.get('username') or not form_data.get('password'):
                flash("Username and password are required.", 'danger')
                return render_template('register.html'), 400

            user_data = UserCreateSchema(username=form_data.get('username'), password=form_data.get('password'))
            UserService.create_user(user_data)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except ValidationError as e:
            errors = e.errors()
            for error in errors:
                flash(f"Validation Error for {error['loc'][0]}: {error['msg']}", 'danger')
        except UserAlreadyExistsError as e:
            flash(str(e), 'danger')
        except Exception as e:
            current_app.logger.error(f"Registration error: {e}", exc_info=True)
            flash('An unexpected error occurred during registration.', 'danger')
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('map.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html'), 400

        user = UserService.check_user_credentials(username, password)
        if user:
            login_user(user, remember=request.form.get('remember') == 'on')
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('map.index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
""",
        os.path.join(base_dir, "aitravel_app", "api", "map_routes.py"): """\
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
        if "AI service is not configured" in info or \
           "Could not retrieve information" in info or \
           "Content generation was blocked" in info:
            return jsonify({"error": info}), 503 # Service Unavailable or specific error
            
        return jsonify({"info": info})
    except ValidationError as e:
        current_app.logger.warning(f"Validation error in get_location_info: {e.errors()}")
        return jsonify({"error": "Validation Error", "details": e.errors()}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_location_info: {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred."}), 500
""",
        os.path.join(base_dir, "aitravel_app", "api", "profile_routes.py"): """\
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
        
        if "AI service is not configured" in recommendation or \
           "Could not generate recommendations" in recommendation or \
           "Content generation was blocked" in recommendation :
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
""",
        # HTML шаблоны остаются в основном такими же, но сообщения об ошибках/предупреждениях
        # в index.html и profile.html могут быть уточнены для Google AI.
        # Я внес небольшие корректировки в эти шаблоны ниже.
        os.path.join(base_dir, "aitravel_app", "templates", "base.html"): """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AI Travel App{% endblock %}</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block head_extra %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="{{ url_for('map.index') }}">AI Travel Planner (Google AI)</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav mr-auto">
                 <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('map.index') }}">Map</a>
                </li>
            </ul>
            <ul class="navbar-nav ml-auto">
                {% if current_user.is_authenticated %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('profile.user_profile') }}">Hi, {{ current_user.username }}! (Profile)</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                    </li>
                {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('auth.register') }}">Register</a>
                    </li>
                {% endif %}
            </ul>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                            <span aria-hidden="true">×</span>
                        </button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>

    <footer class="footer mt-auto py-3 bg-light text-center">
        <div class="container">
            <span class="text-muted">AI Travel App © 2024-2025</span>
        </div>
    </footer>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    {% block scripts_extra %}{% endblock %}
</body>
</html>
""",
        os.path.join(base_dir, "aitravel_app", "templates", "index.html"): """\
{% extends "base.html" %}
{% block title %}Home - AI Travel Map (Google AI){% endblock %}

{% block head_extra %}
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
            crossorigin=""></script>
    <style>
        #map { min-height: 500px; height: 70vh; }
        #info-box { margin-top: 15px; padding: 15px; border: 1px solid #ddd; background-color: #f8f9fa; border-radius: 5px; }
        .leaflet-popup-content-wrapper { border-radius: 5px; }
    </style>
{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h2 class="mb-3">Interactive Travel Map (Powered by Google AI)</h2>
        {% if ai_service_configured %}
        <p>Click on the map to get AI-powered information about any location!</p>
        {% else %}
        <div class="alert alert-warning">
            The AI information feature (Google AI) is currently unavailable. Please ensure the Google API key is set by the administrator.
        </div>
        {% endif %}
        <div id="map"></div>
        <div id="info-box" style="display:none;">
            <h4>Location Information:</h4>
            <p id="info-content" class="mb-0"></p>
        </div>
    </div>
</div>

{% if current_user.is_authenticated %}
<div class="row mt-3">
    <div class="col-md-12">
        <h4>Like this location?</h4>
        <form id="like-place-form" method="POST" action="{{ url_for('profile.like_place_route') }}" style="display:none;">
            <input type="hidden" name="latitude" id="form-latitude">
            <input type="hidden" name="longitude" id="form-longitude">
            <div class="form-group">
                <label for="form-city-name">City Name / Description:</label>
                <input type="text" class="form-control" id="form-city-name" name="city_name" required placeholder="e.g., Eiffel Tower, Paris">
            </div>
            <button type="submit" class="btn btn-success">Like this Place</button>
        </form>
    </div>
</div>
{% endif %}

{% endblock %}

{% block scripts_extra %}
<script>
    document.addEventListener('DOMContentLoaded', function () {
        var map = L.map('map').setView([20, 0], 2); 

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        var popup = L.popup({ closeButton: true, autoClose: false, closeOnClick: false });
        var currentMarker;
        var aiServiceConfigured = {{ ai_service_configured | tojson }};


        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;
                map.setView([lat, lon], 13);
                // Do not add marker automatically for user location to avoid confusion with clicked points
            }, function() {
                console.warn("Geolocation failed or was denied.");
            });
        } else {
            console.warn("Geolocation is not supported by this browser.");
        }

        function onMapClick(e) {
            var lat = e.latlng.lat.toFixed(6);
            var lon = e.latlng.lng.toFixed(6);

            if (currentMarker) {
                 map.removeLayer(currentMarker);
            }
            currentMarker = L.marker([lat, lon]).addTo(map);
            
            popup
                .setLatLng(e.latlng)
                .setContent("Clicked: Lat " + lat + ", Lon " + lon + "<br>Fetching info...")
                .openOn(map);

            document.getElementById('info-box').style.display = 'block';
            document.getElementById('info-content').innerHTML = '<em>Loading AI insights...</em>';

            {% if current_user.is_authenticated %}
            const likeForm = document.getElementById('like-place-form');
            if (likeForm) {
                likeForm.style.display = 'block';
                document.getElementById('form-latitude').value = lat;
                document.getElementById('form-longitude').value = lon;
                document.getElementById('form-city-name').value = ""; 
                document.getElementById('form-city-name').placeholder = "Describe this point (e.g., Park at " + lat + "," + lon + ")";
            }
            {% endif %}

            if (!aiServiceConfigured) {
                document.getElementById('info-content').innerHTML = 'Google AI service is not available.';
                popup.setContent("<b>Clicked:</b> Lat " + lat + ", Lon " + lon + "<br>Google AI service unavailable.");
                return;
            }

            fetch("{{ url_for('map.get_location_info_route') }}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ latitude: parseFloat(lat), longitude: parseFloat(lon) }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || `HTTP error ${response.status}`) });
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    document.getElementById('info-content').innerHTML = "<strong class='text-danger'>Error:</strong> " + data.error;
                    popup.setContent("<b>Error:</b> " + data.error.substring(0,100) + "...");
                } else {
                    document.getElementById('info-content').innerText = data.info;
                    popup.setContent("<b>Google AI Info:</b><br>" + data.info.substring(0,150) + (data.info.length > 150 ? "..." : ""));
                }
            })
            .catch(error => {
                console.error('Error fetching location info:', error);
                document.getElementById('info-content').innerHTML = "<strong class='text-danger'>Failed to fetch information.</strong> " + error.message;
                popup.setContent("<b>Failed to fetch information.</b>");
            });
        }

        map.on('click', onMapClick);
    });
</script>
{% endblock %}
""",
        os.path.join(base_dir, "aitravel_app", "templates", "login.html"): """\
{% extends "base.html" %}
{% block title %}Login - AI Travel App{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h2 class="mb-0">Login</h2>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('auth.login', next=request.args.get('next')) }}">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <div class="form-group form-check">
                        <input type="checkbox" class="form-check-input" id="remember" name="remember">
                        <label class="form-check-label" for="remember">Remember me</label>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Login</button>
                </form>
            </div>
            <div class="card-footer text-center">
                New user? <a href="{{ url_for('auth.register') }}">Register here</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""",
        os.path.join(base_dir, "aitravel_app", "templates", "register.html"): """\
{% extends "base.html" %}
{% block title %}Register - AI Travel App{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h2 class="mb-0">Register</h2>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('auth.register') }}">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required minlength="3">
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required minlength="6">
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">Register</button>
                </form>
            </div>
            <div class="card-footer text-center">
                Already have an account? <a href="{{ url_for('auth.login') }}">Login here</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""",
        os.path.join(base_dir, "aitravel_app", "templates", "profile.html"): """\
{% extends "base.html" %}
{% block title %}My Profile - {{ current_user.username }}{% endblock %}

{% block content %}
<div class="card">
    <div class="card-header">
        <h2>Welcome, {{ current_user.username }}!</h2>
    </div>
    <div class="card-body">
        <div class="mb-4">
            <h4>Your Liked Places:</h4>
            {% if liked_places %}
                <ul class="list-group">
                    {% for place in liked_places %}
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <span>{{ place.city_name }} <small class="text-muted">(Lat: {{ "%.4f"|format(place.latitude) }}, Lon: {{ "%.4f"|format(place.longitude) }})</small></span>
                        </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>You haven't liked any places yet. Go to the <a href="{{ url_for('map.index') }}">map</a> to explore and like locations!</p>
            {% endif %}
        </div>

        <hr>

        <div class="mt-4">
            <h4>Google AI Travel Recommendations:</h4>
            {% if recommendation %}
                 {% if "AI service is not configured" in recommendation or "Could not generate recommendations" in recommendation or "Not enough liked places" in recommendation or "Content generation was blocked" in recommendation %}
                    <div class="alert alert-info">{{ recommendation }}</div>
                 {% else %}
                    <div class="card bg-light">
                        <div class="card-body">
                            <p class="card-text" style="white-space: pre-wrap;">{{ recommendation }}</p> {# white-space: pre-wrap для сохранения форматирования ответа AI #}
                        </div>
                    </div>
                 {% endif %}
            {% else %}
                <p>Like some places first to get personalized travel recommendations from Google AI!</p>
            {% endif %}
        </div>
    </div>
    <div class="card-footer">
        <a href="{{ url_for('map.index') }}" class="btn btn-primary">Explore Map</a>
    </div>
</div>
{% endblock %}
""",
        os.path.join(base_dir, "aitravel_app", "static", "css", "style.css"): """\
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding-bottom: 60px; /* Height of the footer */
    background-color: #f4f7f6;
}
.navbar { margin-bottom: 20px; }
.container { max-width: 1140px; }
.card-header h2, .card-header h4 { margin-bottom: 0; }
.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    height: 60px; 
    line-height: 60px; 
    background-color: #f5f5f5;
}
.alert { border-left-width: 5px; }
.alert-success { border-left-color: #28a745; }
.alert-danger { border-left-color: #dc3545; }
.alert-warning { border-left-color: #ffc107; }
.alert-info { border-left-color: #17a2b8; }
.leaflet-popup-content-wrapper {
    background: #fff;
    box-shadow: 0 3px 14px rgba(0,0,0,0.4);
    border-radius: 5px;
}
.leaflet-popup-content { margin: 13px 19px; font-size: 1.1em; line-height: 1.4; }
.leaflet-popup-tip { background: #fff; }
""",
    os.path.join(base_dir, "aitravel_app", "static", "js", "main.js"): """\
document.addEventListener('DOMContentLoaded', function() {
    console.log("AI Travel App (Google AI) Main JS Initialized");
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
});
""",
    os.path.join(base_dir, ".flaskenv"): """\
FLASK_APP=run.py
FLASK_DEBUG=1
""",
    os.path.join(base_dir, "instance", ".gitkeep"): "",
    os.path.join(base_dir, "migrations", "README"): "This directory is for Flask-Migrate database migrations.\n1. Set your SQLALCHEMY_DATABASE_URI in .env.\n2. Run `flask db init` (only once per project).\n3. Run `flask db migrate -m \"Initial database setup\"`.\n4. Run `flask db upgrade`.\nFor changes: `flask db migrate -m \"Describe changes\"` then `flask db upgrade`.",
    }

    for file_path, content in files.items():
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        if file_path.endswith("run.py"):
            current_permissions = os.stat(file_path).st_mode
            os.chmod(
                file_path,
                current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            )

    print(f"Project '{project_name}' created successfully with Google AI integration.")
    print(f"Path to project: {os.path.abspath(base_dir)}")
    print("\nNext steps:")
    print(f"1. cd {project_name}")
    print("2. Create a virtual environment: python -m venv venv")
    print("3. Activate it:")
    print("   - Windows:   venv\\Scripts\\activate")
    print("   - Linux/macOS: source venv/bin/activate")
    print("4. Install dependencies: pip install -r requirements.txt")
    print("5. IMPORTANT: Your GOOGLE_API_KEY is already set in .env based on your input.")
    print("   - Ensure this key is active and has the 'Generative Language API' (or similar for Gemini models) enabled in your Google Cloud Console.")
    print("   - Review SQLALCHEMY_DATABASE_URI in .env if you want to change the DB location/type.")
    print("6. Database initialization (using Flask-Migrate):")
    print("   a. flask db init")
    print("   b. flask db migrate -m \"Initial database setup\"")
    print("   c. flask db upgrade")
    print("7. Run the application: python run.py")

if __name__ == "__main__":
    create_project_structure()