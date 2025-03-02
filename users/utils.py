import os

from django.core.mail import send_mail
from sendgrid import SendGridAPIClient, Mail
import logging
from .models import Users
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

def reset_user_password(user:Users):
    user

    subject = "Reset Your Password"
    message = f"Hello {user.full_name},\n\nPlease click the link below to reset your password.\n\n{os.getenv('FRONTEND_URL')}/reset-password/{user.password_reset_code}"
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    except Exception as e:
        logger.error("Failed to send email", exc_info=True)
        raise e

