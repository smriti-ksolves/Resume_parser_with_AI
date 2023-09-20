import os

from app.db.resume_model import resume_data
from app.app import logger
from app.models.get_resume_data import get_data


def get_all_cadidate_with_skills(params, jd_data):
    try:
        user_id = int(params.get("user_id"))
        email = params.get("email")

        # Extract the minimum experience requirement from jd_data
        min_exp = jd_data.get("min_exp", 0)  # Default to 0 if not specified

        candidate_data_objects = resume_data.query \
            .filter_by(user_id=user_id, email=email) \
            .with_entities(resume_data.id, resume_data.candidate_data) \
            .all()

        candidate_data_list = [
            {
                "candidate_id": data[0],
                "candidate_data": data[1],
            }
            for data in candidate_data_objects
        ]

        # Filter out candidates with total_experience >= min_exp
        filtered_candidates = [
            candidate for candidate in candidate_data_list
            if candidate["candidate_data"]["total_experience"] >= min_exp
        ]

        return filtered_candidates

    except Exception as err:
        logger.error(str(err))
        return None


def match_jb_skills_with_candidate(params, jd_data):
    candidates = get_all_cadidate_with_skills(params, jd_data)
    qualification_thres = float(os.getenv("QUALIFICATION_PERCENTAGE_THRESHOLD"))
    results = []  # To store the results for each candidate

    jb_skills = jd_data.get("skills", [])
    # Calculate the total count of jb_skills
    total_jb_skills = len(jb_skills)

    if candidates is None:
        return None  # Handle the case when candidates are not found

    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        candidate_data = candidate["candidate_data"]

        total_experience = candidate_data.get("total_experience", 0)
        company_counts = candidate_data.get("company_counts", 1)  # Default to 1 if not available

        # Assuming candidate_data is in JSON format with a "skills" field
        candidate_skills = candidate_data.get("skills", [])

        # Calculate the score by counting the common skills between jd_skills and candidate_skills
        common_skills = len(set(jb_skills) & set(candidate_skills))

        # Calculate current_score by counting the common skills between jd_skills and current_skills (if available)
        current_skills = candidate_data.get("current_skills", [])
        current_score = len(set(jb_skills) & set(current_skills))

        # Calculate the stability based on the provided formula stability = (total_experience / company_counts) * (
        # 100 / total_experience) if total_experience > 0 else 0 if company_counts else 0

        # Calculate the percentage of score and current_score based on the count of jb_skills
        score_percentage = (common_skills / total_jb_skills) * 100
        current_score_percentage = (current_score / total_jb_skills) * 100

        total_score = score_percentage + current_score_percentage  # + stability

        if score_percentage >= qualification_thres:
            # Create a result dictionary for this candidate
            result = {
                "candidate_id": candidate_id,
                "skills": candidate_skills,
                "current_skills": current_skills,
                "score": common_skills,
                "current_score": current_score,
                # "stability_score": stability,
                "score_percentage": score_percentage,
                "current_score_percentage": current_score_percentage,
                "total_score": total_score
            }

            results.append(result)

    # Sort the results based on score (descending) and then current_score
    sorted_results = sorted(results,
                            key=lambda x: (-x["total_score"], -x["score_percentage"], -x["current_score_percentage"]))

    return sorted_results


def get_filtered_candidate_ids(sorted_data):
    if sorted_data is not None:
        # Extract candidate IDs and return as a list
        candidate_ids = [candidate["candidate_id"] for candidate in sorted_data]
        return candidate_ids

    return []


def candidate_filtering_proc(params, jd_data):
    try:
        user_id = int(params["user_id"])
        email = params["email"]
        print(jd_data)
        candidate_data = match_jb_skills_with_candidate(params, jd_data)
        print(candidate_data)
        candidate_ids = get_filtered_candidate_ids(candidate_data)
        print(candidate_ids)
        if candidate_ids:
            final_candidate_data = get_data(user_id, email, id_list=candidate_ids)
            print(final_candidate_data)
            return final_candidate_data
        return {}
    except Exception as err:
        return {"error": str(err)}
