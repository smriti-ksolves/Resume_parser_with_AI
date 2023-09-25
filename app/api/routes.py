from flask import Blueprint, jsonify, request, render_template, make_response
from flask_cors import cross_origin
import os
from app.db.user_model import login_user
from app.models.get_resume_data import get_data, delete_candidate_row
from app.models.questions_generator import question_validator_and_generator, jd_parser
from app.models.sign_up import signup_user
from app.models.sign_in import signin_user
from app.models.resume_parser_controler import get_extracted_data
from app.models.put_presign_url import generate_presigned_url
from app.app import logger, db
from functools import wraps
import jwt
import time
from app.app import flask_app
from app.helper.candidate_filter_out_with_skills import candidate_filtering_proc

api_routes = Blueprint('api', __name__)


# Define your routes using the blueprint
@api_routes.route('/')
@cross_origin(supports_credentials=False)
def index():
    data = {
        "message": "Server Started ...",
    }
    logger.info("Server Running!")
    return make_response(jsonify(data), 200)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return make_response(jsonify({'error': 'Token is missing!'}), 401)
        try:
            data = jwt.decode(token, flask_app.config['SECRET_KEY'], algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            return make_response(jsonify({'error': 'Token has expired!'}), 401)
        except jwt.InvalidTokenError:
            return make_response(jsonify({'error': 'Invalid token!'}), 401)

        return f(*args, **kwargs)

    return decorated


@api_routes.route('/verify_email', methods=['GET'])
def verify_email():
    sign_url = os.getenv("SIGN_IN_URL")
    sign_up_url = os.getenv("SIGN_UP_URL")
    token = request.args.get('token')
    if not token:
        return render_template('signup.html', custom_url=sign_up_url)

    user = login_user.query.filter_by(verification_token=token).first()
    if not user:
        return render_template('signup.html', custom_url=sign_up_url)

    # Mark the user's email as verified
    user.email_verified = True
    user.verification_token = None  # Clear the token after verification
    db.session.commit()

    return render_template('signin.html', custom_url=sign_url)


@api_routes.route('/signup', methods=['POST'])
def signup():
    """
        Endpoint for user signup.

        Handles the registration of a new user by expecting a JSON payload containing user information.

        Parameters:
            - first_name (str): The first name of the user.
            - last_name (str): The last name of the user.
            - email (str): The email address of the user.
            - phone_number (str): The phone number of the user.
            - country (str): The country of the user.
            - password (str): The password chosen by the user.
            - organization_name (str): The name of the user's organization.
            - organization_address (str): The address of the user's organization.
            - number_of_employees (int): The number of employees in the user's organization.

        Returns:
            dict: A JSON response containing the result of the signup process.
    """
    try:
        params = request.json
        response = signup_user(params)
        return response

    except KeyError as err:
        return make_response(jsonify({"error": f"Missing key in request JSON: {err}"}), 400)  # HTTP 400 Bad Request

    except ValueError as err:
        return make_response(jsonify({"error": f"Invalid value in request JSON: {err}"}), 400)  # HTTP 400 Bad Request

    except Exception as err:
        return make_response(jsonify({"error": f"An error occurred: {err}"}), 500)  # HTTP 500 Internal Server Error


@api_routes.route('/signin', methods=['POST'])
def signin():
    """
       Endpoint for user sign-in.

       This endpoint handles user authentication through sign-in. It expects a JSON payload
       containing user credentials such as email and password.

       Returns:
           dict: A JSON response containing the result of the sign-in process.
       """
    try:
        params = request.json
        response = signin_user(params)
        return response
    except Exception as err:
        return make_response(jsonify({"error": str(err)}), 500)


@api_routes.route('/get_parsed_data', methods=['POST'])
# @token_required
def resume_parsing():
    """
      Endpoint for parsing resumes and creating JSON data.

      This endpoint handles the parsing of uploaded resume files and creates JSON data
      containing the extracted information. It expects a JSON payload containing parameters
      for the parsing process and uploaded resume files.

      Parameters: - params (dict): A dictionary containing parameters for the parsing process. Example parameters may
      include settings for data extraction. - files (File): One or more uploaded resume files (PDFs) for processing.

      Returns:
          dict: A JSON response containing the result of the parsing and JSON data creation process.
      """
    try:
        start_time = time.time()
        params = request.json
        data = get_extracted_data(params)
        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(f"Processing Time for {len(data)} - resume parsing is {processing_time}")
        return make_response(jsonify({"data": data}), 200)

    except Exception as e:
        logger.error(e)
        return make_response(jsonify({"error": "An error occurred during resume parsing."}), 500)  # Internal Server
        # Error status code


@api_routes.route('/get_presigned_url', methods=['POST'])
# @token_required
def presigned_url_generation():
    folder_name = os.environ.get("FOLDER_NAME")
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    params = request.json
    presigned_url_list = []
    try:
        for file in params["file_names"]:
            if file:
                try:
                    object_key = os.path.join(folder_name, file)
                    presigned_url = generate_presigned_url(bucket_name, object_key)
                    if presigned_url is not None:
                        presigned_url_list.append(presigned_url)
                    else:
                        presigned_url_list.append({})
                except:
                    presigned_url_list.append({})
        return make_response(jsonify({"presigned_urls": presigned_url_list}), 200)

    except Exception as err:
        logger.error(f"An error occurred while generating presigned URL: {err}")
        return make_response(jsonify({"error": "An error occurred while generating presigned URL."}), 500)


@api_routes.route('/get_candidate_data', methods=['GET'])
# @token_required
def get_candidate_data():
    """
    API endpoint to retrieve candidate data based on user_id and email.

    This API endpoint expects query parameters "user_id" and "email".
    The function get_data is called to retrieve candidate data.

    Returns:
        JSON response containing candidate data or error message.
    """
    try:
        user_id = request.args.get('user_id')
        email = request.args.get('email')
        data = get_data(user_id, email)

        if "error" in data:
            logger.error(data)
            return make_response(jsonify(data), 500)

        else:
            return make_response(jsonify(data), 200)
    except Exception as err:
        return make_response(jsonify({"error": str(err)}), 500)


@api_routes.route('/delete_candidate_record/<candidate_id>', methods=['DELETE'])
# @token_required
def delete_row(candidate_id):
    """
    API endpoint to delete a candidate record.

    This API endpoint receives a JSON payload containing the "candidate_id" to be deleted.
    The function delete_candidate_row is called to perform the deletion.

    Returns:
        JSON response indicating success or error.
    """
    try:
        candidate_id = int(candidate_id)  # Convert to integer
    except (ValueError, TypeError):
        return make_response(jsonify({"error": "Invalid candidate_id"}), 400)
    res = delete_candidate_row(candidate_id)
    if "error" in res:
        logger.error(res)
        return make_response(jsonify(res), 500)
    else:
        return make_response(jsonify(res), 200)


@api_routes.route('/generate_questions', methods=['POST'])
# @token_required
def get_interview_quest():
    """
        Generate Interview Questions API Endpoint.

        This endpoint generates interview questions based on the provided parameters.

        Endpoint: POST /generate_questions

        Requires a valid JWT token for authentication.

        Args:
            None

        Returns:
            tuple: A tuple containing the JSON response data and the HTTP status code.

            Response Format:
            {
                "question": "What is the correct syntax for defining a function in Python?",
                "options": [
                    "func();",
                    "def func();",
                    "funct() ->",
                    "def funct;"
                ],
                "answer": 1
            }

            Status Codes:
            - 200 OK: Successful request.
            - 400 Bad Request: Invalid input or error occurred during processing.
            - 401 Unauthorized: Token is missing or invalid.
    """
    try:
        params = request.json
        data = question_validator_and_generator(params)
        if "error" in data:
            return make_response(jsonify(data), 500)
        return make_response(jsonify(data), 200)
    except Exception as err:
        return make_response(jsonify({"error": str(err)}), 500)


@api_routes.route('/JD_Parser', methods=['POST'])
# @token_required
def get_jb_data():
    """
    Endpoint to parse JD (Job Description) data, filter candidates, and return candidate data.

    Args:
        None (assumes data is passed in the request JSON body).

    Returns:
        JSON response:
        - If successful, returns a JSON object containing candidate data.
        - If there's an error in parsing or candidate filtering, returns an error message with an appropriate HTTP status code.
    """
    try:
        params = request.json
        # Check if all required parameters are present
        required_params = ["JD_Des"]  # "user_id", #"email",
        if not all(param in params for param in required_params):
            return make_response(jsonify({"error": "Missing parameters"}), 400)

        data = jd_parser(params)
        if "error" in data:
            return make_response(jsonify(data), 500)
        # candidate_data = candidate_filtering_proc(params, data)
        # if "error" in candidate_data:
        #     return make_response(jsonify(candidate_data), 500)

        else:
            return make_response(jsonify({"data": data}), 200)

    except Exception as err:
        return make_response(jsonify({"error": str(err)}), 500)
