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
