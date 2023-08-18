from app.app import db
from datetime import datetime


class resume_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('login_user.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    candidate_data = db.Column(db.JSON(240), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
