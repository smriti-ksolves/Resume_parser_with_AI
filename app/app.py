import logging
import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import boto3

dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)
log_level = os.environ.get("LOG_LEVEL", 'INFO')
log_path = os.environ.get("LOG_PATH", '/var/log/ai.log')
logging.basicConfig(format='%(asctime)s %(levelname)s: %(filename)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=log_level,
                    handlers=[logging.FileHandler(log_path), logging.StreamHandler()])

logger = logging.getLogger(__name__)


def create_app():
    # Create the Flask application instance
    server = Flask(__name__)
    # Register API routes
    return server


db_user = os.environ.get("DB_USER")
user_password = os.environ.get("USER_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME")

# Create the Flask application
flask_app = create_app()
flask_app.logger = logger
flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{user_password}@{db_host}/{db_name}'
db = SQLAlchemy(flask_app)
bcrypt = Bcrypt(flask_app)
flask_app.config['SECRET_KEY'] = 'c67a86ac99fc779a9d4af8f4a4d576b8194f392ba4449244b5ad13858b855b13'
jwt = JWTManager(flask_app)

# for s3 bucket
access_key = os.environ.get("AWS_ACCESS_KEY_ID")
access_secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
region = os.environ.get("S3_REGION")
flask_app.config['S3_BUCKET_NAME'] = os.environ.get("S3_BUCKET_NAME")

flask_app.config['AWS_ACCESS_KEY_ID'] = access_key
flask_app.config['AWS_SECRET_ACCESS_KEY'] = access_secret

s3_client = boto3.client('s3', aws_access_key_id=access_key,
                         aws_secret_access_key=access_secret,
                         region_name=region
                         )
