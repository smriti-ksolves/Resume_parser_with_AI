from app.db.resume_model import resume_data
from app.app import flask_app, db


def resume_data_create(params, data):
    user_id = params.get("user_id")
    email = params.get("email")
    if not user_id or not email or not data:
        return {'error': 'All fields are required.'}

    username = email.split('@')[0]
    new_data = resume_data(user_id=user_id, username=username, email=email, candidate_data=data)

    db.session.add(new_data)
    db.session.commit()

    return {'message': 'Candidate Data Added successfully.'}
