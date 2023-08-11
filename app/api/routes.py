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

       This endpoint handles the registration of a new user. It expects a JSON payload
       containing user information such as first name, last name, email, phone number,
       country, password, organization name, organization address, and number of employees.

       Args:
           None (Relies on request.json to get payload)

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
    # params = request.jsong
    data = get_extracted_data(params)
    response = resume_data_create(params, data)
    return jsonify(response)
