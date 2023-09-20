from app.app import flask_app, db, bcrypt
from app.db.user_model import login_user
from app.helper.mail_vertification import generate_verification_token, send_verification_email, \
    resend_verification_email
from datetime import datetime, timedelta
from flask import jsonify, make_response


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

    # Define the list of required fields
    required_fields = ["first_name", "last_name", "email", "phone_number", "country", "password", "org_name",
                       "org_address", "no_emp"]

    # Check if any required fields are missing
    missing_fields = [field for field in required_fields if not params.get(field)]

    if missing_fields:
        return make_response(jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400)

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
    existing_user = login_user.query.filter_by(email=email).first()
    if existing_user:
        if existing_user.email_verified:
            return make_response(jsonify({'error': 'Email is already registered.'}), 400)  # HTTP 400 Bad Request
        else:
            if existing_user.verification_token_expiry and existing_user.verification_token_expiry < datetime.utcnow():
                # Resend verification email with a new token and update expiration time
                return resend_verification_email(email)
            else:
                return make_response(jsonify({"error": "Email not verified. An email has already been sent to your "
                                                       "account. Please check your email and verify your account."}),
                                     401)

    if login_user.query.filter_by(phone_number=phone_number).first():
        return make_response(jsonify({'error': 'Phone is already registered.'}), 400)  # HTTP 400 Bad Request

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
    res = send_verification_email(email, verification_token)
    if res:
        return make_response(jsonify({'success': 'A verification email has been sent to your email address. Please '
                                                 'check your inbox and spam folder.'}), 200)  # HTTP 200 OK

    else:
        return make_response(jsonify({'error': 'Error sending email'}), 500)  # HTTP 500 Internal Server Error
