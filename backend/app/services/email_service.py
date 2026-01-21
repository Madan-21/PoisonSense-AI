# Email Service - Send verification emails and OTPs
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
import hashlib

from app.core.config import settings

# In-memory OTP storage (use Redis in production)
otp_storage = {}

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))

def generate_verification_token(email: str) -> str:
    """Generate a verification token for email"""
    timestamp = datetime.utcnow().isoformat()
    data = f"{email}{timestamp}{settings.SECRET_KEY}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]

def store_otp(email: str, otp: str) -> None:
    """Store OTP with expiration time"""
    expiry = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    otp_storage[email.lower()] = {
        "otp": otp,
        "expiry": expiry,
        "attempts": 0
    }

def verify_otp(email: str, otp: str) -> tuple[bool, str]:
    """Verify OTP for email"""
    email = email.lower()
    
    if email not in otp_storage:
        return False, "No OTP found. Please request a new one."
    
    stored = otp_storage[email]
    
    # Check expiry
    if datetime.utcnow() > stored["expiry"]:
        del otp_storage[email]
        return False, "OTP has expired. Please request a new one."
    
    # Check attempts (max 3)
    if stored["attempts"] >= 3:
        del otp_storage[email]
        return False, "Too many failed attempts. Please request a new OTP."
    
    # Verify OTP
    if stored["otp"] != otp:
        stored["attempts"] += 1
        remaining = 3 - stored["attempts"]
        return False, f"Invalid OTP. {remaining} attempts remaining."
    
    # Success - remove OTP
    del otp_storage[email]
    return True, "Email verified successfully!"

def clear_otp(email: str) -> None:
    """Clear OTP for email"""
    email = email.lower()
    if email in otp_storage:
        del otp_storage[email]

def get_email_html_template(otp: str, full_name: str) -> str:
    """Generate HTML email template for OTP"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); border-radius: 10px 10px 0 0;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 28px;">🏥 PoisonSense AI</h1>
                                <p style="margin: 10px 0 0 0; color: #ffffff; opacity: 0.9;">Email Verification</p>
                            </td>
                        </tr>
                        
                        <!-- Body -->
                        <tr>
                            <td style="padding: 40px;">
                                <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Hello {full_name}! 👋</h2>
                                <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                    Thank you for registering with PoisonSense AI. To complete your registration and verify your email address, please use the verification code below:
                                </p>
                                
                                <!-- OTP Box -->
                                <div style="background-color: #f8f9fa; border: 2px dashed #dc3545; border-radius: 10px; padding: 30px; text-align: center; margin: 30px 0;">
                                    <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px;">Your Verification Code</p>
                                    <h1 style="margin: 0; color: #dc3545; font-size: 48px; letter-spacing: 10px; font-weight: bold;">{otp}</h1>
                                </div>
                                
                                <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px;">
                                    ⏰ This code will expire in <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.
                                </p>
                                <p style="margin: 0 0 20px 0; color: #666666; font-size: 14px;">
                                    🔒 If you didn't request this code, please ignore this email.
                                </p>
                                
                                <!-- Features -->
                                <div style="background-color: #fff3cd; border-radius: 8px; padding: 20px; margin-top: 30px;">
                                    <h3 style="margin: 0 0 15px 0; color: #856404; font-size: 16px;">🚨 With PoisonSense AI, you can:</h3>
                                    <ul style="margin: 0; padding: 0 0 0 20px; color: #856404; font-size: 14px; line-height: 1.8;">
                                        <li>Get instant poison identification from symptoms</li>
                                        <li>Find nearest emergency services</li>
                                        <li>Access first-aid protocols</li>
                                        <li>Contact poison control centers 24/7</li>
                                    </ul>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 30px 40px; background-color: #f8f9fa; border-radius: 0 0 10px 10px; text-align: center;">
                                <p style="margin: 0 0 10px 0; color: #999999; font-size: 12px;">
                                    This is an automated message from PoisonSense AI.
                                </p>
                                <p style="margin: 0; color: #999999; font-size: 12px;">
                                    © 2026 PoisonSense AI. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def get_email_text_template(otp: str, full_name: str) -> str:
    """Generate plain text email template for OTP"""
    return f"""
PoisonSense AI - Email Verification

Hello {full_name}!

Thank you for registering with PoisonSense AI.

Your verification code is: {otp}

This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.

If you didn't request this code, please ignore this email.

---
PoisonSense AI
Your Emergency Poison Response Assistant
    """

async def send_verification_email(email: str, full_name: str) -> tuple[bool, str]:
    """Send OTP verification email"""
    
    # Check if SMTP is configured
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        # Development mode - return OTP directly
        otp = generate_otp()
        store_otp(email, otp)
        return True, f"DEV_MODE: Your OTP is {otp} (Email not configured)"
    
    try:
        # Generate OTP
        otp = generate_otp()
        store_otp(email, otp)
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔐 PoisonSense AI - Verify Your Email (Code: {otp})"
        msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = email
        
        # Attach both plain text and HTML versions
        text_part = MIMEText(get_email_text_template(otp, full_name), "plain")
        html_part = MIMEText(get_email_html_template(otp, full_name), "html")
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, email, msg.as_string())
        
        return True, "Verification code sent to your email!"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Email service authentication failed. Please contact support."
    except smtplib.SMTPException as e:
        return False, f"Failed to send email: {str(e)}"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

async def send_welcome_email(email: str, full_name: str) -> tuple[bool, str]:
    """Send welcome email after successful verification"""
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return True, "Welcome email skipped (Email not configured)"
    
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 40px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 40px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0;">✅ Welcome to PoisonSense AI!</h1>
                </div>
                <div style="padding: 40px;">
                    <h2 style="color: #333;">Hello {full_name}! 🎉</h2>
                    <p style="color: #666; line-height: 1.6;">
                        Your email has been verified successfully! You now have full access to PoisonSense AI.
                    </p>
                    <div style="background: #e8f5e9; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #2e7d32; margin-top: 0;">What you can do now:</h3>
                        <ul style="color: #2e7d32; line-height: 1.8;">
                            <li>🤖 Use AI-powered poison identification</li>
                            <li>🏥 Find nearest hospitals & poison centers</li>
                            <li>📋 Access emergency first-aid protocols</li>
                            <li>📞 Quick-dial emergency services</li>
                        </ul>
                    </div>
                    <p style="color: #999; font-size: 14px;">
                        Stay safe! The PoisonSense AI Team
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "✅ Welcome to PoisonSense AI - Account Verified!"
        msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = email
        
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, email, msg.as_string())
        
        return True, "Welcome email sent!"
        
    except Exception as e:
        # Don't fail registration if welcome email fails
        return True, f"Welcome email failed but registration complete: {str(e)}"
