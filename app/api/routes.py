from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import os
from app.models.sign_up import signup_user
from app.models.sign_in import signin_user
from app.models.resume_parser_controler import get_extracted_data
from app.models.put_presign_url import generate_presigned_url
from app.app import logger

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
        params = request.json
        data = get_extracted_data(params)

        return jsonify(data), 200

    except Exception as e:
        logger.error(e)
        return jsonify({"error": "An error occurred during resume parsing."}), 500  # Internal Server Error status code


@api_routes.route('/get_presigned_url', methods=['POST'])
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
