from app.models.resumedata import resume_data


def get_data(params):
    try:
        user_id = params.get('user_id')
        email = params.get('email')

        if user_id is None or email is None:
            return {'error': 'Both user_id and email are required as query parameters.'}
        candidate_data_objects = resume_data.query.filter_by(user_id=user_id, email=email).order_by(
            resume_data.created_at).with_entities(resume_data.candidate_data).all()

        candidate_data_list = [data[0] for data in candidate_data_objects]

        return candidate_data_list

    except Exception as e:
        return {'error': str(e)}
