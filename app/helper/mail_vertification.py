from app.app import mail
import secrets
from flask import url_for
from flask_mail import Message
from app.app import flask_app


def generate_verification_token():
    return secrets.token_urlsafe(32)


def send_verification_email(email, verification_token):
    hostname = flask_app.config['HOST_NAME']  # Replace 'HOSTNAME' with the actual configuration key
    port = flask_app.config['PORT']  # Replace 'PORT' with the actual configuration key
    verification_link = url_for('api.verify_email', token=verification_token, _external=True, _scheme='http',
                                _port=port, _external_host=hostname)
    subject = 'Verify Your Email'
    recipients = [email]

    message_body = f"Click the following link to verify your email: {verification_link}"

    message = Message(subject=subject, recipients=recipients, body=message_body)
    mail.send(message)
