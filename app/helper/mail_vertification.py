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
    subject = 'Confirm Your Email Address - HelpingHR'
    recipients = email

    message_body = f"Click the following link to verify your email: {verification_link}"

    # message = Message(subject=subject, recipients=recipients, body=message_body)
    # mail.send(message)
    # Create a SendGrid message
    html_body = f"""
          <!DOCTYPE html>
          <html>
          <head>
              <title>Verify Your Email</title>
          </head>
          <body>
              <p>Dear User,</p>
              <p>Thank you for registering with HelpingHR. To complete your registration and start using our services, please click the button below to verify your email address:</p>
              <p style="text-align: center;">
                  <a href="{verification_link}" style="background-color: #007BFF; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
              </p>
              <p>If you did not sign up for HelpingHR, please disregard this email.</p>
              <p>Thank you,</p>
              <p>HelpingHR Team</p>
          </body>
          </html>
          """
    logger.info(f'{verification_link}')
    message = Mail(
        from_email='smriti.tiwari@ksolves.com',  # Replace with your sender email
        to_emails=recipients,
        subject=subject,
        html_content=html_body,
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
