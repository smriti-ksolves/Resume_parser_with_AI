from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.app import jwt, bcrypt
from app.db.user_model import login_user
from datetime import datetime, timedelta


def signin_user(data):
    """
    Sign in a user and generate an access token.

    This function takes user data (email and password), checks the provided credentials against the database,
    and if valid, generates an access token for the user's identity.

    Args:
        data (dict): A dictionary containing user data.
            Expected keys: "email" (str), "password" (str).

    Returns:
        dict: An access token and user ID if the credentials are valid, or an error message if invalid.
    """
    email = data.get('email')
    password = data.get('password')

    # Query the database for a user with the provided email
    user = login_user.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        # Check if the email is verified
        if not user.email_verified:
            return {'error': 'Email not verified. Please check your email for a verification link.'}

        # Check for expired verification tokens
        if user.verification_token_expiry and user.verification_token_expiry < datetime.utcnow():
            return {'error': 'Verification token has expired. Please request a new verification link.'}

        # Generate an access token for the user's identity
        access_token = create_access_token(identity=user.id)

        return {'access_token': access_token, "user_id": user.id, "username": user.first_name}
    else:
        return {'error': 'Invalid credentials.'}
