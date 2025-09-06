# utils/email_utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email, otp, otp_type, user_name=None):
    """
    Send OTP email to user
    """
    try:
        # Email subject based on OTP type
        subjects = {
            'email_verification': 'Verify Your Email Address',
            'password_reset': 'Password Reset Code',
        }
        
        subject = subjects.get(otp_type, 'Email Verification Code')
        
        # Email context
        context = {
            'otp': otp,
            'user_name': user_name or 'User',
            'otp_type': otp_type,
            'expiry_minutes': 10,
        }
        
        # Render email template
        html_message = render_to_string('emails/otp_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"OTP email sent successfully to {email} for {otp_type}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        return False


def send_welcome_email(email, user_name):
    """
    Send welcome email after successful registration
    """
    try:
        subject = 'Welcome to Our Platform!'
        
        context = {
            'user_name': user_name,
        }
        
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        return False


def send_password_reset_success_email(email, user_name):
    """
    Send confirmation email after successful password reset
    """
    try:
        subject = 'Password Reset Successful'
        
        context = {
            'user_name': user_name,
        }
        
        html_message = render_to_string('emails/password_reset_success.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset success email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset success email to {email}: {str(e)}")
        return False
