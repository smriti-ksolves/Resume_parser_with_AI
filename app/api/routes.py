from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import json
from app.models.sign_up import signup_user
from app.models.sign_in import signin_user
from app.models.resumedata import resume_data_create
from app.models.resume_parser_controler import get_extracted_data

api_routes = Blueprint('api', __name__)


# Define your routes using the blueprint
@api_routes.route('/')
@cross_origin(supports_credentials=False)
def index():
    data = {
        "message": "Server Started ...",
    }
    return jsonify(data)


@api_routes.route('/signup', methods=['POST'])
def signup():
    """
        Endpoint for user signup.

        Handles the registration of a new user by expecting a JSON payload containing user information.

        Parameters:
            None (Relies on request.json to obtain the following payload fields):
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

    params = json.loads(request.json.decode("utf-8"))
    # params = request.json
    response = signup_user(params)
    return jsonify(response)


@api_routes.route('/signin', methods=['POST'])
def signin():
    """
       Endpoint for user sign-in.

       This endpoint handles user authentication through sign-in. It expects a JSON payload
       containing user credentials such as email and password.

       Returns:
           dict: A JSON response containing the result of the sign-in process.
       """
    params = json.loads(request.json.decode("utf-8"))
    # params = request.json
    response = signin_user(params)
    return jsonify(response)


@api_routes.route('/get_parsed_data', methods=['POST'])
def resume_parsing():
    params = json.loads(request.json.decode("utf-8"))
    # files = request.files['files']
    # params = request.json
    data = get_extracted_data(params)
    response = resume_data_create(params, data)
    return jsonify(response)
