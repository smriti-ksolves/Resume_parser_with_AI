from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.app import jwt, bcrypt
from app.db.user_model import login_user

def signin_user(data):

    email = data.get('email')
    password = data.get('password')
    user = login_user.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token,"user_id":user.id}
    else:
        return {'error': 'Invalid credentials.'}
