from app.db.resume_model import resume_data
from app.app import flask_app, db,logger


def resume_data_create(params, data):
    """
    Create and store candidate resume data.

    This function takes parameters `params` and candidate `data`, and creates a new entry in the database
    for the candidate's resume data. The provided user ID, email, and data are used to populate the entry.

    Args:
        params (dict): A dictionary containing user-related parameters.
            Expected keys: "user_id" (int), "email" (str).
        data (dict): A dictionary containing candidate resume data.

    Returns:
        dict: A message indicating the success of the operation or an error message.
    """
    user_id = params.get("user_id")
    email = params.get("email")

    # Check if all required fields are provided
    if not user_id or not email or not data:
        return {'error': 'All fields are required.'}

    # Extract username from the email
    username = email.split('@')[0]

    # Create a new entry with candidate resume data
    new_data = resume_data(user_id=user_id, username=username, email=email, candidate_data=data)

    # Add the new entry to the database and commit changes
    db.session.add(new_data)
    db.session.commit()
    logger.info("Candidate Data Added successfully")
    return {'message': 'Candidate Data Added successfully.'}
