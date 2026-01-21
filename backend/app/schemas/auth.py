# Auth schemas
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

# Valid email domains (common ones)
VALID_EMAIL_DOMAINS = {
    # Common email providers
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com',
    'icloud.com', 'me.com', 'mac.com', 'aol.com', 'protonmail.com',
    'proton.me', 'zoho.com', 'mail.com', 'gmx.com', 'yandex.com',
    # Country-specific
    'yahoo.co.in', 'yahoo.co.uk', 'hotmail.co.uk', 'outlook.co.uk',
    'rediffmail.com', 'yahoo.com.np', 'gmail.co.in',
    # Educational
    'edu', 'ac.in', 'edu.np',
    # Organizational
    'org', 'gov', 'gov.np', 'org.np',
    # Custom domains (allow any .com, .org, .net, .io, .co)
}

# Valid TLDs (Top Level Domains)
VALID_TLDS = {
    'com', 'org', 'net', 'edu', 'gov', 'io', 'co', 'in', 'np', 'uk',
    'us', 'ca', 'au', 'de', 'fr', 'jp', 'cn', 'ru', 'br', 'mx',
    'info', 'biz', 'me', 'tv', 'app', 'dev', 'tech', 'online',
    'store', 'shop', 'site', 'xyz', 'ai'
}

def validate_email_domain(email: str) -> str:
    """Validate email domain and TLD"""
    if not email or '@' not in email:
        raise ValueError('Invalid email format')
    
    domain = email.split('@')[1].lower()
    
    # Check if it's a known valid domain
    if domain in VALID_EMAIL_DOMAINS:
        return email
    
    # Extract TLD (last part after the last dot)
    parts = domain.split('.')
    if len(parts) < 2:
        raise ValueError('Invalid email domain')
    
    tld = parts[-1]
    
    # Check for valid TLD
    if tld not in VALID_TLDS:
        raise ValueError(f'Invalid email domain extension ".{tld}". Please use a valid email address.')
    
    # Check for common typos in domains
    common_typos = {
        'gmial.com': 'gmail.com',
        'gmal.com': 'gmail.com', 
        'gamil.com': 'gmail.com',
        'gmail.comm': 'gmail.com',
        'gmail.con': 'gmail.com',
        'gmail.co': 'gmail.com',
        'yahooo.com': 'yahoo.com',
        'yahoo.comm': 'yahoo.com',
        'yahoo.con': 'yahoo.com',
        'hotmal.com': 'hotmail.com',
        'hotmail.comm': 'hotmail.com',
        'hotmail.con': 'hotmail.com',
        'outlok.com': 'outlook.com',
        'outlook.comm': 'outlook.com',
    }
    
    if domain in common_typos:
        raise ValueError(f'Did you mean {common_typos[domain]}? Please check your email domain.')
    
    return email

def validate_password_strength(password: str) -> str:
    """Validate password strength"""
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        raise ValueError('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        raise ValueError('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one number')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)')
    
    return password

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_email_domain(v)

class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_email_domain(v)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        # Remove spaces and dashes for validation
        cleaned = re.sub(r'[\s\-]', '', v)
        # Check if it starts with + and has digits, or just digits
        if not re.match(r'^\+?\d{10,15}$', cleaned):
            raise ValueError('Phone number must be 10-15 digits, optionally starting with +')
        return v
    
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Email Verification Schemas
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_email_domain(v)
    
    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError('OTP must contain only digits')
        return v

class ResendOTPRequest(BaseModel):
    email: EmailStr
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_email_domain(v)

class SignupResponse(BaseModel):
    message: str
    email: str
    requires_verification: bool = True

class VerificationResponse(BaseModel):
    message: str
    verified: bool
    access_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserResponse] = None
