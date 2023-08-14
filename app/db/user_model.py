from app.app import db


class login_user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    country = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    org_name = db.Column(db.String(120), nullable=False)
    org_address = db.Column(db.String(50), nullable=False)
    no_of_emp = db.Column(db.String(120), nullable=False)

