import logging
import os

from app.app import mail
import secrets
from flask import url_for
from flask_mail import Message
from app.app import flask_app, sg
from sendgrid.helpers.mail import Mail
from app.app import logger


def generate_verification_token():
    return secrets.token_urlsafe(32)


def send_verification_email(email, verification_token):
    # hostname = flask_app.config['HOST_NAME']  # Replace 'HOSTNAME' with the actual configuration key
    # port = flask_app.config['PORT']  # Replace 'PORT' with the actual configuration key
    # public_url = flask_app.config['PUBLIC_URL']
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
        from_email='smt444441@gmail.com',  # Replace with your sender email
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
