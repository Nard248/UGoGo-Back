import os

from django.core.mail import send_mail
from sendgrid import SendGridAPIClient, Mail

from ugogo import settings

def send_verification_email(user):
    user.generate_verification_code()

    subject = "Your Email Verification Code"
    message = f"Hello {user.full_name},\n\nYour email verification code is: {user.email_verification_code}\n\nThis code expires in 10 minutes."

    message = Mail(
        from_email='from_email@example.com',
        to_emails='to@example.com',
        subject=subject,
        html_content=message)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))
    # send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])