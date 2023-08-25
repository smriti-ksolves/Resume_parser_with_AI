from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import os
from app.models.get_resume_data import get_data, delete_candidate_row
from app.models.questions_generator import question_validator_and_generator, jd_parser
from app.models.sign_up import signup_user
from app.models.sign_in import signin_user
from app.models.resume_parser_controler import get_extracted_data
from app.models.put_presign_url import generate_presigned_url
from app.app import logger
from functools import wraps
import jwt
import time
from app.app import flask_app

api_routes = Blueprint('api', __name__)


# Define your routes using the blueprint
@api_routes.route('/')
@cross_origin(supports_credentials=False)
def index():
    data = {
        "message": "Server Started ...",
    }
    logger.info("Server Running!")
    return jsonify(data)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, flask_app.config['SECRET_KEY'], algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated


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

    params = request.json
    response = signup_user(params)
    if 'error' in response:
        return jsonify(response), 400  # Bad Request status code
    else:
        return jsonify(response), 201  # Created status code


@api_routes.route('/signin', methods=['POST'])
def signin():
    """
       Endpoint for user sign-in.

       This endpoint handles user authentication through sign-in. It expects a JSON payload
       containing user credentials such as email and password.

       Returns:
           dict: A JSON response containing the result of the sign-in process.
       """
    params = request.json
    response = signin_user(params)
    if 'error' in response:
        return jsonify(response), 401  # Unauthorized status code
    else:
        return jsonify(response), 200  # OK status code


@api_routes.route('/get_parsed_data', methods=['POST'])
@token_required
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
        return jsonify({"data": data, "processing_time": processing_time}), 200

    except Exception as e:
        logger.error(e)
        return jsonify({"error": "An error occurred during resume parsing."}), 500  # Internal Server Error status code


@api_routes.route('/get_presigned_url', methods=['POST'])
@token_required
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
        return jsonify({"presigned_urls": presigned_url_list}), 200

    except Exception as err:
        logger.error(f"An error occurred while generating presigned URL: {err}")
        return jsonify({"error": "An error occurred while generating presigned URL."}), 500


@api_routes.route('/get_candidate_data', methods=['GET'])
@token_required
def get_candidate_data():
    """
    API endpoint to retrieve candidate data based on user_id and email.

    This API endpoint expects query parameters "user_id" and "email".
    The function get_data is called to retrieve candidate data.

    Returns:
        JSON response containing candidate data or error message.
    """
    user_id = request.args.get('user_id')
    email = request.args.get('email')
    data = get_data(user_id, email)

    if "error" in data:
        logger.error(data)
        return jsonify(data), 400

    else:
        return jsonify(data), 200


@api_routes.route('/delete_candidate_record/<candidate_id>', methods=['DELETE'])
@token_required
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
        return jsonify({"error": "Invalid candidate_id"}), 400
    res = delete_candidate_row(candidate_id)
    if "error" in res:
        logger.error(res)
        return jsonify(res), 400
    else:
        return jsonify(res), 200


@api_routes.route('/generate_questions', methods=['POST'])
@token_required
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
    params = request.json
    data = question_validator_and_generator(params)
    if "error" in data:
        return jsonify(data), 400
    return jsonify(data), 200


@api_routes.route('/JD_Parser', methods=['POST'])
@token_required
def get_jb_data():
    try:
        params = request.json
        data = jd_parser(params)
        if "error" in data:
            return jsonify(data), 400
        return jsonify(data), 200
    except Exception as err:
        return jsonify({"error": str(err)}), 500
