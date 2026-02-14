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
from app.db.session import SessionLocal
from app.models.otp import OTPRecord


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))


def generate_verification_token(email: str) -> str:
    """Generate a verification token for email"""
    timestamp = datetime.utcnow().isoformat()
    data = f"{email}{timestamp}{settings.SECRET_KEY}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


def store_otp(email: str, otp: str) -> None:
    """Store OTP with expiration time in Postgres."""
    expiry = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    db = SessionLocal()
    try:
        # Delete any existing OTP for this email
        db.query(OTPRecord).filter(OTPRecord.email == email.lower()).delete()
        record = OTPRecord(email=email.lower(), otp=otp, expires_at=expiry, attempts=0)
        db.add(record)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def verify_otp(email: str, otp: str) -> tuple[bool, str]:
    """Verify OTP for email using Postgres."""
    email = email.lower()
    db = SessionLocal()
    try:
        record = db.query(OTPRecord).filter(OTPRecord.email == email).first()

        if not record:
            return False, "No OTP found. Please request a new one."

        # Check expiry
        if datetime.utcnow() > record.expires_at:
            db.delete(record)
            db.commit()
            return False, "OTP has expired. Please request a new one."

        # Check attempts (max 3)
        if record.attempts >= 3:
            db.delete(record)
            db.commit()
            return False, "Too many failed attempts. Please request a new OTP."

        # Verify OTP
        if record.otp != otp:
            record.attempts += 1
            db.commit()
            remaining = 3 - record.attempts
            return False, f"Invalid OTP. {remaining} attempts remaining."

        # Success — remove OTP
        db.delete(record)
        db.commit()
        return True, "Email verified successfully!"
    except Exception:
        db.rollback()
        return False, "Verification error. Please try again."
    finally:
        db.close()


def clear_otp(email: str) -> None:
    """Clear OTP for email."""
    email = email.lower()
    db = SessionLocal()
    try:
        db.query(OTPRecord).filter(OTPRecord.email == email).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

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
        # Development mode - still generate OTP but don't show it
        otp = generate_otp()
        store_otp(email, otp)
        return True, f"DEV_MODE: Your OTP is {otp}"
    
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
        
        return True, "Verification code sent to your email! Please check your inbox and spam folder."
        
    except smtplib.SMTPAuthenticationError:
        return False, "Email service authentication failed. Please contact support."
    except smtplib.SMTPException as e:
        return False, f"Failed to send email: {str(e)}"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

async def send_welcome_email(email: str, full_name: str) -> tuple[bool, str]:
    """Send welcome email after successful OTP verification (account still pending admin approval)"""
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return True, "Welcome email skipped (Email not configured)"
    
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 40px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 40px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0;">⏳ PoisonSense AI - Account Under Review</h1>
                </div>
                <div style="padding: 40px;">
                    <h2 style="color: #333;">Hello {full_name}! 👋</h2>
                    <p style="color: #666; line-height: 1.6;">
                        Your email has been verified successfully! Your account is now <strong>pending admin approval</strong>.
                    </p>
                    <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #856404; margin-top: 0;">⏳ What happens next?</h3>
                        <ul style="color: #856404; line-height: 1.8;">
                            <li>Our admin team will review your registration details</li>
                            <li>This typically takes <strong>24-48 hours</strong></li>
                            <li>You will receive an email once your account is approved</li>
                            <li>After approval, you can log in and access all features</li>
                        </ul>
                    </div>
                    <p style="color: #666; line-height: 1.6;">
                        Please do <strong>not</strong> try to log in until you receive the approval notification. 
                        If you have any questions, contact our support team.
                    </p>
                    <p style="color: #999; font-size: 14px;">
                        Thank you for your patience! — The PoisonSense AI Team
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "⏳ PoisonSense AI - Account Under Review"
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


async def send_approval_email(email: str, full_name: str) -> tuple[bool, str]:
    """Send email notification when admin approves a user account"""
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return True, "Approval email skipped (Email not configured)"
    
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 40px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); padding: 40px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0;">✅ Account Approved!</h1>
                    <p style="color: #ffffff; opacity: 0.9; margin: 10px 0 0 0;">PoisonSense AI</p>
                </div>
                <div style="padding: 40px;">
                    <h2 style="color: #333;">Hello {full_name}! 🎉</h2>
                    <p style="color: #666; line-height: 1.6;">
                        Great news! Your <strong>PoisonSense AI</strong> account has been reviewed and <strong style="color: #16a34a;">approved</strong> by our admin team.
                    </p>
                    <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;">
                        <h3 style="color: #166534; margin-top: 0;">🚀 You can now log in!</h3>
                        <p style="color: #166534; margin-bottom: 0;">
                            Visit PoisonSense AI and sign in with your registered email and password to access all features.
                        </p>
                    </div>
                    <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin-top: 20px;">
                        <h3 style="color: #333; margin-top: 0;">🏥 What you can do now:</h3>
                        <ul style="color: #666; line-height: 1.8; padding-left: 20px;">
                            <li>Get instant poison identification from symptoms</li>
                            <li>Find nearest emergency services</li>
                            <li>Access first-aid protocols</li>
                            <li>Contact poison control centers 24/7</li>
                            <li>Use AI-powered analysis tools</li>
                        </ul>
                    </div>
                    <p style="color: #999; font-size: 14px; margin-top: 30px;">
                        Thank you for joining PoisonSense AI! — The PoisonSense AI Team
                    </p>
                </div>
                <div style="padding: 20px 40px; background-color: #f8f9fa; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; color: #999; font-size: 12px;">
                        © 2026 PoisonSense AI. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "✅ PoisonSense AI - Your Account Has Been Approved!"
        msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = email
        
        # Plain text version
        text_content = f"""
PoisonSense AI - Account Approved!

Hello {full_name}!

Great news! Your PoisonSense AI account has been approved by our admin team.

You can now log in with your registered email and password to access all features.

Thank you for joining PoisonSense AI!
— The PoisonSense AI Team
        """
        
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, email, msg.as_string())
        
        return True, "Approval email sent!"
        
    except Exception as e:
        # Don't fail approval if email fails
        return False, f"Approval email failed: {str(e)}"


async def send_rejection_email(email: str, full_name: str) -> tuple[bool, str]:
    """Send email notification when admin rejects a user account"""
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return True, "Rejection email skipped (Email not configured)"
    
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 40px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 40px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0;">❌ Account Not Approved</h1>
                    <p style="color: #ffffff; opacity: 0.9; margin: 10px 0 0 0;">PoisonSense AI</p>
                </div>
                <div style="padding: 40px;">
                    <h2 style="color: #333;">Hello {full_name},</h2>
                    <p style="color: #666; line-height: 1.6;">
                        We regret to inform you that your <strong>PoisonSense AI</strong> account registration has <strong style="color: #dc2626;">not been approved</strong> after review by our admin team.
                    </p>
                    <div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #991b1b; margin-top: 0;">Possible reasons:</h3>
                        <ul style="color: #991b1b; line-height: 1.8; padding-left: 20px;">
                            <li>Incomplete or invalid registration documents</li>
                            <li>Unable to verify professional credentials</li>
                            <li>Missing or unclear license document</li>
                        </ul>
                    </div>
                    <p style="color: #666; line-height: 1.6;">
                        If you believe this was a mistake, you may register again with valid documentation or contact our support team for assistance.
                    </p>
                    <p style="color: #999; font-size: 14px; margin-top: 30px;">
                        — The PoisonSense AI Team
                    </p>
                </div>
                <div style="padding: 20px 40px; background-color: #f8f9fa; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; color: #999; font-size: 12px;">
                        © 2026 PoisonSense AI. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "❌ PoisonSense AI - Account Registration Update"
        msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = email
        
        # Plain text version
        text_content = f"""
PoisonSense AI - Account Not Approved

Hello {full_name},

We regret to inform you that your PoisonSense AI account registration has not been approved after review by our admin team.

If you believe this was a mistake, you may register again with valid documentation or contact our support team for assistance.

— The PoisonSense AI Team
        """
        
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, email, msg.as_string())
        
        return True, "Rejection email sent!"
        
    except Exception as e:
        # Don't fail rejection if email fails
        return False, f"Rejection email failed: {str(e)}"


async def send_password_reset_email(email: str, full_name: str) -> tuple[bool, str]:
    """Send OTP for password reset"""

    # Generate and store OTP
    otp = generate_otp()
    store_otp(email, otp)

    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        # Dev mode – return OTP in message so frontend can display it
        return True, f"DEV_MODE: Your OTP is {otp}"

    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f4f4f4;">
            <table role="presentation" style="width:100%;border-collapse:collapse;">
                <tr><td align="center" style="padding:40px 0;">
                    <table role="presentation" style="width:600px;border-collapse:collapse;background:#fff;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,.1);">
                        <tr><td style="padding:40px;text-align:center;background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);border-radius:10px 10px 0 0;">
                            <h1 style="margin:0;color:#fff;font-size:28px;">🔒 PoisonSense AI</h1>
                            <p style="margin:10px 0 0;color:#fff;opacity:.9;">Password Reset</p>
                        </td></tr>
                        <tr><td style="padding:40px;">
                            <h2 style="margin:0 0 20px;color:#333;font-size:24px;">Hello {full_name}! 👋</h2>
                            <p style="margin:0 0 20px;color:#666;font-size:16px;line-height:1.6;">
                                We received a request to reset your password. Use the code below to set a new password:
                            </p>
                            <div style="background:#f8f9fa;border:2px dashed #f59e0b;border-radius:10px;padding:30px;text-align:center;margin:30px 0;">
                                <p style="margin:0 0 10px;color:#666;font-size:14px;">Your Reset Code</p>
                                <h1 style="margin:0;color:#d97706;font-size:48px;letter-spacing:10px;font-weight:bold;">{otp}</h1>
                            </div>
                            <p style="margin:0 0 10px;color:#666;font-size:14px;">⏰ This code expires in <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.</p>
                            <p style="margin:0;color:#666;font-size:14px;">🔒 If you didn't request this, please ignore this email. Your password will remain unchanged.</p>
                        </td></tr>
                        <tr><td style="padding:30px 40px;background:#f8f9fa;border-radius:0 0 10px 10px;text-align:center;">
                            <p style="margin:0;color:#999;font-size:12px;">© 2026 PoisonSense AI. All rights reserved.</p>
                        </td></tr>
                    </table>
                </td></tr>
            </table>
        </body>
        </html>
        """

        text_content = f"""
PoisonSense AI - Password Reset

Hello {full_name}!

Your password reset code is: {otp}

This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.
If you didn't request this, please ignore this email.

— PoisonSense AI
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔒 PoisonSense AI - Password Reset Code: {otp}"
        msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = email

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, email, msg.as_string())

        return True, "Password reset code sent to your email! Check your inbox and spam folder."

    except smtplib.SMTPAuthenticationError:
        return False, "Email service authentication failed. Please contact support."
    except smtplib.SMTPException as e:
        return False, f"Failed to send email: {str(e)}"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
