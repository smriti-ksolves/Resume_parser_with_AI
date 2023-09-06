import logging
import os
from app.db.user_model import login_user
from datetime import datetime, timedelta
from app.app import mail
import secrets
from flask import url_for
from flask_mail import Message
from app.app import flask_app, sg, db
from sendgrid.helpers.mail import Mail
from app.app import logger


def generate_verification_token():
    return secrets.token_urlsafe(32)


def send_verification_email(email, verification_token):
    # hostname = flask_app.config['HOST_NAME']  # Replace 'HOSTNAME' with the actual configuration key
    # port = flask_app.config['PORT']  # Replace 'PORT' with the actual configuration key
    # public_url = flask_app.config['PUBLIC_URL']
    from_email = os.getenv("MAIL_USERNAME")
    base_url = os.getenv("BASE_URL")
    verification_link = rf"{base_url}verify_email?token={verification_token}"
    subject = 'Welcome to HelpingHR - Verify Your Email Address'
    recipients = email

    message_body = f"Click the following link to verify your email: {verification_link}"

    # message = Message(subject=subject, recipients=recipients, body=message_body)
    # mail.send(message)
    # Create a SendGrid message
    # Load the email template from the HTML file
    with open("app/templates/mail_content.html", "r") as template_file:
        email_content = template_file.read()
    email_content = email_content.replace("{{ verification_link }}", verification_link)

    logger.info(f'{verification_link}')
    message = Mail(
        from_email=from_email,  # Replace with your sender email
        to_emails=recipients,
        subject=subject,
        html_content=email_content,
    )
    # Send the email
    try:
        response = sg.send(message)
        if response.status_code == 202:
            return True  # Email sent successfully
        else:
            return False  # Email sending failed
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        return False  # Email sending failed


def resend_verification_email(email):
    """
    Resend the verification email with a new token and update the token expiration time.

    Args:
        email (str): The email address of the user.

    Returns:
        dict: A success message if the email is sent successfully, or an error message if there's an issue.
    """
    user = login_user.query.filter_by(email=email).first()

    if user:
        # Generate a new verification token and update the expiration time
        new_verification_token = generate_verification_token()
        new_verification_token_expiry = datetime.utcnow() + timedelta(hours=24)  # Set a new expiration time

        user.verification_token = new_verification_token
        user.verification_token_expiry = new_verification_token_expiry

        db.session.commit()

        # Send the new verification email
        res = send_verification_email(email, new_verification_token)
        if res:
            return {'success': 'A new verification email has been sent to your email address. '
                               'Please check your inbox and spam folder.'}
        else:
            return {'error': 'Error sending the new verification email.'}
    else:
        return {'error': 'User not found.'}
