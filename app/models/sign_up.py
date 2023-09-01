from app.app import flask_app, db, bcrypt
from app.db.user_model import login_user
from app.helper.mail_vertification import generate_verification_token, send_verification_email
from datetime import datetime, timedelta


def signup_user(params):
    """
      Sign up a new user.

      This function takes user parameters, validates them, and creates a new user entry in the database
      if the provided information is valid and unique.

      Args:
          params (dict): A dictionary containing user registration parameters.
              Expected keys: "first_name" (str), "last_name" (str), "email" (str), "phone_number" (str),
                             "country" (str), "password" (str), "org_name" (str), "org_address" (str),
                             "no_emp" (int, optional).

      Returns:
          dict: A message indicating the success of the user creation or an error message.
    """
    first = params.get("first_name")
    last = params.get("last_name")
    email = params.get('email')
    phone_number = params.get('phone_number')
    country = params.get('country')
    password = params.get('password')
    org_name = params.get("org_name")
    org_address = params.get("org_address")
    no_emp = params.get("no_emp")
    username = email.split('@')[0]

    # Check if email is already registered
    if login_user.query.filter_by(email=email).first():
        return {'error': 'Email is already registered.'}

    if login_user.query.filter_by(phone_number=phone_number).first():
        return {'error': 'Phone is already registered.'}

    # Validate input
    if not username or not email or not phone_number or not country or not password:
        return {'error': 'All fields are required.'}

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Generate a verification token and calculate expiration time
    verification_token = generate_verification_token()
    verification_token_expiry = datetime.utcnow() + timedelta(hours=24)  # Set an expiration time (e.g., 24 hours)

    # Create a new user instance
    new_user = login_user(first_name=first, last_name=last, username=username, email=email, phone_number=phone_number,
                          country=country, password=hashed_password, org_name=org_name, org_address=org_address,
                          no_of_emp=no_emp, verification_token=verification_token,
                          verification_token_expiry=verification_token_expiry)

    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()
    # Send verification email (you'll need to implement the send_verification_email function)
    send_verification_email(email, verification_token)
    return {'message': 'User created successfully.'}
