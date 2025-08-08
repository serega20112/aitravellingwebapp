from flask_migrate import Migrate
from src.backend.infrastructure.db.db import db

migrate = Migrate(db=db)
