# Login / Signup with Email Verification
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import ValidationError
import os
import uuid

from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    UserSignup, UserLogin, Token, LoginResponse, UserResponse,
    VerifyOTPRequest, ResendOTPRequest, SignupResponse, VerificationResponse,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_active_user
)
from app.core.config import settings
from app.services.email_service import (
    send_verification_email, 
    verify_otp, 
    send_welcome_email,
    clear_otp,
    send_password_reset_email
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Temporary storage for unverified users (use Redis in production)
pending_users = {}

@router.post("/signup", response_model=SignupResponse)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """
    Register a new user account - Step 1: Send OTP
    
    Requirements:
    - Valid email address with proper domain (gmail.com, yahoo.com, etc.)
    - Password: minimum 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
    - Full name: 2-255 characters
    - Phone (optional): 10-15 digits
    
    After signup, user will receive an OTP via email to verify their account.
    """
    email = user_data.email.lower()
    
    # Check if email already exists and is verified
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        if existing_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please login instead."
            )
        else:
            # User exists but not verified - resend OTP
            success, message = await send_verification_email(email, existing_user.full_name)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=message
                )
            return SignupResponse(
                message=message,
                email=email,
                requires_verification=True
            )
    
    # Store user data temporarily until verified
    pending_users[email] = {
        "email": email,
        "password": user_data.password,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "role": user_data.role if user_data.role else "patient",
        "registration_number": user_data.registration_number,
        "specialization": user_data.specialization,
        "experience_years": user_data.experience_years,
        "hospital_address": user_data.hospital_address,
        "created_at": datetime.utcnow()
    }
    
    # Send verification email
    success, message = await send_verification_email(email, user_data.full_name)
    
    if not success:
        # Clean up on failure
        if email in pending_users:
            del pending_users[email]
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return SignupResponse(
        message=message,
        email=email,
        requires_verification=True
    )

@router.post("/verify-otp", response_model=VerificationResponse)
async def verify_email_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Verify email with OTP - Step 2: Complete Registration
    
    After successful verification, user account is created and access token is returned.
    """
    email = data.email.lower()
    
    # Check if already registered and verified
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user and existing_user.is_verified:
        return VerificationResponse(
            message="Email already verified. Please login.",
            verified=True
        )
    
    # Verify OTP
    is_valid, message = verify_otp(email, data.otp)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Get pending user data
    if email not in pending_users and not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration session expired. Please signup again."
        )
    
    # Create or update user
    if existing_user:
        # Update existing unverified user
        existing_user.is_verified = True
        existing_user.admin_approved = False  # Needs admin approval
        existing_user.updated_at = datetime.utcnow()
        user = existing_user
    else:
        # Create new user from pending data
        user_data = pending_users[email]
        
        # Map role string to UserRole enum
        role_str = user_data.get("role", "patient").lower()
        if role_str == "doctor":
            user_role = UserRole.DOCTOR
        elif role_str in ["hospital", "hospital_admin"]:
            user_role = UserRole.HOSPITAL_ADMIN
        else:
            user_role = UserRole.PATIENT
        
        user = User(
            email=email,
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            phone=user_data["phone"],
            role=user_role,
            registration_number=user_data.get("registration_number"),
            specialization=user_data.get("specialization"),
            experience_years=user_data.get("experience_years"),
            hospital_address=user_data.get("hospital_address"),
            is_active=True,
            is_verified=True,
            admin_approved=False,  # Requires admin approval
            created_at=datetime.utcnow()
        )
        db.add(user)
        
        # Clean up pending user
        del pending_users[email]
    
    db.commit()
    db.refresh(user)
    
    # Send welcome email (async, don't wait)
    await send_welcome_email(email, user.full_name)
    
    # Return success message WITHOUT access token
    return VerificationResponse(
        message="Email verified successfully! Your account is pending admin approval. You will be able to login within 24 hours after verification.",
        verified=True,
        access_token=None,  # No token - user must wait for approval
        token_type=None,
        user=None  # Don't return user data yet
    )

@router.post("/resend-otp")
async def resend_otp(data: ResendOTPRequest, db: Session = Depends(get_db)):
    """
    Resend OTP to email
    """
    email = data.email.lower()
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == email).first()
    
    if existing_user and existing_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified. Please login."
        )
    
    # Get name from pending users or existing unverified user
    full_name = "User"
    if email in pending_users:
        full_name = pending_users[email]["full_name"]
    elif existing_user:
        full_name = existing_user.full_name
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending registration found. Please signup first."
        )
    
    # Clear old OTP and send new one
    clear_otp(email)
    success, message = await send_verification_email(email, full_name)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return {"message": message, "email": email}

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password (OAuth2 compatible)
    """
    # Find user (case-insensitive email)
    user = db.query(User).filter(User.email == form_data.username.lower()).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Check email verification
    if not user.is_verified:
        # Send new OTP
        success, message = await send_verification_email(user.email, user.full_name)
        
        # Check if email service is not configured (manual verification required)
        if not success and "24 hours" in message:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending verification. This typically takes up to 24 hours. You will receive a notification once your account is verified."
            )
        
        error_detail = "Email not verified. A new verification code has been sent to your email."
        
        # Include OTP in message for dev mode
        if "DEV_MODE" in message:
            error_detail = f"Email not verified. {message}"
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail
        )
    
    # Check admin approval
    if not user.admin_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending admin approval. Please wait 24-48 hours. You will receive an email notification once approved."
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/login/json", response_model=LoginResponse)
async def login_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with JSON body (for frontend convenience)
    """
    user = db.query(User).filter(User.email == user_data.email.lower()).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Check email verification
    if not user.is_verified:
        # Send new OTP
        success, message = await send_verification_email(user.email, user.full_name)
        error_detail = "Email not verified. A new verification code has been sent to your email."
        
        # Include OTP in message for dev mode
        if "DEV_MODE" in message:
            error_detail = f"Email not verified. {message}"
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_detail
        )
    
    # Check admin approval
    if not user.admin_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending admin approval. Please wait 24-48 hours. You will receive an email notification once approved."
        )
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user's info
    """
    return UserResponse.model_validate(current_user)

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout (client should discard token)
    """
    return {"message": "Successfully logged out"}


@router.post("/upload-license")
async def upload_license(
    email: str = Form(...),
    license_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload license/registration document for a pending user.
    Called right after OTP verification during signup.
    Accepts PDF, JPG, JPEG, PNG files up to 5MB.
    """
    email = email.lower()
    
    # Validate file type
    allowed_types = {"application/pdf", "image/jpeg", "image/jpg", "image/png"}
    if license_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, JPG, and PNG files are allowed."
        )
    
    # Read file content and check size (5MB limit)
    content = await license_file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB."
        )
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # Create upload directory
    upload_dir = os.path.join(os.getcwd(), settings.LICENSE_UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    ext = os.path.splitext(license_file.filename)[1] or ".pdf"
    unique_name = f"{user.id}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(upload_dir, unique_name)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Store relative path in database
    relative_path = f"{settings.LICENSE_UPLOAD_DIR}/{unique_name}"
    user.license_document = relative_path
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "License document uploaded successfully.",
        "file_path": relative_path
    }


# ── Password Reset ──────────────────────────────────────────────────

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Forgot password — Step 1: Send OTP to the user's registered email.
    """
    email = data.email.lower()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address. Please check the email or sign up for a new account.",
        )

    # Send password-reset OTP
    success, message = await send_password_reset_email(email, user.full_name)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message,
        )

    # For dev mode, forward the DEV_MODE message to the frontend
    return {"message": message, "email": email}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password — Step 2: Verify OTP and set a new password.
    """
    email = data.email.lower()

    # Verify the OTP
    is_valid, message = verify_otp(email, data.otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    # Reject if new password is the same as the current one
    if verify_password(data.new_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as your current password. Please choose a different password.",
        )

    # Update password
    user.hashed_password = get_password_hash(data.new_password)
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Password reset successfully! You can now log in with your new password."}
