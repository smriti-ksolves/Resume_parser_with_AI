from app.app import flask_app, db, bcrypt
from app.db.user_model import login_user


def signup_user(params):
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

    # Create a new user instance
    new_user = login_user(first_name=first, last_name=last, username=username, email=email, phone_number=phone_number,
                          country=country, password=hashed_password, org_name=org_name, org_address=org_address,
                          no_of_emp=no_emp)

    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()

    return {'message': 'User created successfully.'}
