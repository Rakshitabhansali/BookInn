import uuid
import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generateRandomToken():
    """Generate a random token for email verification"""
    return str(uuid.uuid4())

def sendEmailToken(email, token):
    """Send email verification token"""
    subject = 'Verify Your Account - BookInn'
    message = f'''
    Hi there,
    
    Thank you for registering with BookInn!
    
    Please click the link below to verify your email address:
    http://127.0.0.1:8000/account/verify-account/{token}/
    
    If you didn't create this account, please ignore this email.
    
    Best regards,
    BookInn Team
    '''

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def sendOTPtoEmail(email, otp):
    """Send OTP via email"""
    subject = 'Your OTP for BookInn Login'
    message = f'''
    Hi there,
    
    Your OTP for login is: {otp}
    
    This OTP is valid for 10 minutes only.
    
    If you didn't request this OTP, please ignore this email.
    
    Best regards,
    BookInn Team
    '''

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        print(f"OTP {otp} sent successfully to {email}")
        return True
    except Exception as e:
        print(f"OTP email sending failed: {str(e)}")
        return False