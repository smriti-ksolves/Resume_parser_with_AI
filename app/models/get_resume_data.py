from app.models.resumedata import resume_data
from app.app import db


def get_data(user_id: int, email: str, id_list: list = []):
    """
    Retrieve candidate data based on user_id, email, and optional id_list.

    Args:
        user_id (int): The user ID to filter candidate data.
        email (str): The email address to filter candidate data.
        id_list (list, optional): List of candidate IDs to further filter. Defaults to [].

    Returns:
        list: A list of dictionaries containing candidate information with "candidate_id" and "candidate_data".
            Example:
            [
                {"candidate_id": 1, "candidate_data": {...}},
                {"candidate_id": 2, "candidate_data": {...}},
                ...
            ]
        dict: An error dictionary in case of an exception, with an "error" key containing the error message.
    """
    try:

        if user_id is None or email is None:
            return {'error': 'Both user_id and email are required as query parameters.'}

        if not id_list:
            candidate_data_objects = resume_data.query.filter_by(user_id=user_id, email=email).order_by(
                resume_data.created_at.desc()).with_entities(resume_data.id, resume_data.candidate_data).all()
        else:
            candidate_data_objects = resume_data.query.filter_by(user_id=user_id, email=email).filter(
                resume_data.id.in_(id_list)).order_by(
                resume_data.created_at.desc()).with_entities(resume_data.id, resume_data.candidate_data).all()
        candidate_data_list = [{"candidate_id": data[0], "candidate_data": data[1]} for data in candidate_data_objects]
        return candidate_data_list

    except Exception as e:
        return {'error': str(e)}


def delete_candidate_row(id_to_delete: int):
    """
    Delete a candidate record based on the provided candidate_id.

    Args:
        id_to_delete (int): The ID of the candidate record to be deleted.

    Returns:
        dict: A dictionary indicating success or error.
    """
    try:
        if id_to_delete is None:
            return {'error': 'Missing parameters'}
        if not isinstance(id_to_delete, int):
            return {'error': 'Invalid candidate_id'}
        deleted_rows = db.session.query(resume_data) \
            .filter_by(id=id_to_delete) \
            .delete(synchronize_session=False)

        db.session.commit()
        if deleted_rows:
            return {"success": f"{deleted_rows} row(s) deleted successfully."}
        else:
            return {"error": f"No record found for {id_to_delete} this candidate ID."}
    except Exception as err:
        return {"error": str(err)}
