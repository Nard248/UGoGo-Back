import os

from django.core.mail import send_mail
from sendgrid import SendGridAPIClient, Mail
import logging

from ugogo import settings

logger = logging.getLogger(__name__)

def send_verification_email(user):
    user.generate_verification_code()

    subject = "Your Email Verification Code"
    message = f"Hello {user.full_name},\n\nYour email verification code is: {user.email_verification_code}\n\nThis code expires in 10 minutes."
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    except Exception as e:
        logger.error("Failed to send email", exc_info=True)
        raise e

