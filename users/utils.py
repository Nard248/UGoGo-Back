import os
from datetime import datetime

from django.core.mail import send_mail
from sendgrid import SendGridAPIClient, Mail
import logging
from django.utils import timezone

from .models import Users, EmailVerificationCode
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

def send_card_verification_email(user, code_generator):
    verification_code = code_generator.generate_code()
    subject = "Your Card Verification Code"
    message = f"Dear {user.full_name},\n\nYou just attapted: {verification_code}\n\nThis code expires in 10 minutes."
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    except Exception as e:
        logger.error("Failed to send email", exc_info=True)
        raise e


def reset_user_password(user:Users):
    subject = "Reset Your Password"
    message = f"Hello {user.full_name},\n\nPlease click the link below to reset your password.\n\n{os.getenv('FRONTEND_URL')}/reset-password/{user.password_reset_code}"
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    except Exception as e:
        logger.error("Failed to send email", exc_info=True)
        raise e

def send_passport_verification_sccuess_email(user:Users):
    subject = "Ugogo - Passport verification"
    message = f"Hello {user.full_name},\n\nYour passport has been verified successfully."
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    except Exception as e:
        logger.error("Failed to send email", exc_info=True)
        raise e

def send_passport_verification_failed_email(user: Users, rejection_reason: str):
    subject = "Ugogo - Passport Verification Failed"
    message = f"Hello {user.full_name},\n\nUnfortunately, your passport verification was unsuccessful.\n\nReason: {rejection_reason}\n\n Your account was deacrtivated please contact support for more information."
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
    except Exception as e:
        logger.error("Failed to send passport verification failure email", exc_info=True)
        raise e

def check_verification_code(verification_code, user):
    existing_code = EmailVerificationCode.objects.filter(
        user=user,
        code=verification_code,
    ).first()


    if not existing_code or existing_code.expires_at < timezone.now():
        raise Exception("No active verification code found.")

    return existing_code