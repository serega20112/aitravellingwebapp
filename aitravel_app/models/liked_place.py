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
