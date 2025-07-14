# Authentication & Profile Management API

This document describes the comprehensive authentication system and user profile management API for the Palenso platform.

## Overview

The authentication system provides:
- User registration and login with email or mobile number
- Email and mobile number verification
- Password reset functionality
- Token-based authentication with JWT
- Comprehensive user profile management

## Models

### User Model
- **id**: Primary key
- **username**: Unique username (auto-generated)
- **email**: Unique email address
- **mobile_number**: Unique mobile number with validation
- **first_name**, **last_name**: User names
- **is_email_verified**: Email verification status
- **is_mobile_verified**: Mobile verification status
- **is_active**: Account status
- **date_joined**: Account creation date
- **last_active**: Last activity timestamp

### Token Model
- **token**: Unique token string
- **token_type**: Type of token (bearer, email_verification, otp_verification, forgot_password)
- **user**: Associated user
- **is_used**: Whether token has been used
- **expires_at**: Token expiration time
- **created_at**: Token creation time
- **used_at**: Token usage time

### Profile Model
- **user**: One-to-one relationship with User
- **bio**: User biography
- **date_of_birth**: Birth date
- **gender**: Gender selection
- **profile_picture**: Profile image
- **website**, **linkedin**, **github**, **twitter**: Social links
- **country**, **state**, **city**: Location information

### Related Models
- **Education**: Educational background
- **WorkExperience**: Work history
- **Skill**: User skills with proficiency levels
- **Interest**: User interests/hobbies
- **Project**: User projects
- **Resume**: User resumes

## SSO-Compatible Authentication Flow

The authentication system now supports both traditional signup and SSO flows with a streamlined verification process.

## Signup Flow

### Step 1: Check Availability
**Endpoint:** `POST /api/auth/check-availability`

Check if email or mobile number is available for registration before proceeding.

**Request Body (Email):**
```json
{
    "email": "john.doe@example.com"
}
```

**Request Body (Mobile):**
```json
{
    "mobile_number": "+1234567890"
}
```

**Response (Available):**
```json
{
    "available": true,
    "email": "john.doe@example.com",
    "message": "Email is available."
}
```

**Response (Not Available):**
```json
{
    "available": false,
    "email": "john.doe@example.com",
    "message": "Email is already registered."
}
```

### Step 2: Create User
**Endpoint:** `POST /api/auth/create-user`

Creates a user account with contact information (without password). The user is created as inactive until the signup process is completed.

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "mobile_number": "+1234567890"
}
```

**Response:**
```json
{
    "user": {
        "id": "uuid",
        "username": "generated_username",
        "email": "john.doe@example.com",
        "mobile_number": "+1234567890",
        "first_name": "John",
        "last_name": "Doe",
        "is_email_verified": false,
        "is_mobile_verified": false,
        "is_active": false,
        "date_joined": "2024-01-01T00:00:00Z",
        "last_active": null
    },
    "message": "User created successfully. Please verify your contact information."
}
```

### Step 3: Send Verification Codes
**Endpoint:** `POST /api/auth/send-verification`

Sends verification codes to either email or mobile number. This endpoint can be used to send initial codes or resend them.

**Request Body (Email):**
```json
{
    "email": "john.doe@example.com"
}
```

**Request Body (Mobile):**
```json
{
    "mobile_number": "+1234567890"
}
```

**Response:**
```json
{
    "message": "Verification email sent successfully."
}
```

### Step 4: Verify Contact Information
**Endpoint:** `POST /api/auth/verify-contact`

Verify both email and mobile in a single request. This streamlines the verification process.

**Request Body:**
```json
{
    "email": "john.doe@example.com",
    "mobile_number": "+1234567890",
    "email_code": "123456",
    "mobile_otp": "789012"
}
```

**Response:**
```json
{
    "user": {
        "id": "uuid",
        "username": "generated_username",
        "email": "john.doe@example.com",
        "mobile_number": "+1234567890",
        "first_name": "John",
        "last_name": "Doe",
        "is_email_verified": true,
        "is_mobile_verified": true,
        "is_active": false,
        "date_joined": "2024-01-01T00:00:00Z",
        "last_active": null
    },
    "message": "Contact verification completed successfully.",
    "ready_for_password": true
}
```

### Step 5: Complete Signup
**Endpoint:** `POST /api/auth/complete-signup`

Completes the signup process by setting the password and activating the user account. Both email and mobile must be verified before this step.

**Request Body:**
```json
{
    "user_id": "uuid-from-step-2",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "access_token": "jwt_access_token",
    "refresh_token": "jwt_refresh_token",
    "user": {
        "id": "uuid",
        "username": "generated_username",
        "email": "john.doe@example.com",
        "mobile_number": "+1234567890",
        "first_name": "John",
        "last_name": "Doe",
        "is_email_verified": true,
        "is_mobile_verified": true,
        "is_active": true,
        "date_joined": "2024-01-01T00:00:00Z",
        "last_active": "2024-01-01T00:00:00Z"
    },
    "message": "Signup completed successfully."
}
```

## SSO Flow Support

The new flow supports SSO integration by allowing:

1. **Availability Check**: Before SSO redirect, check if user exists
2. **User Creation**: Create user account if not exists
3. **Verification**: Verify contact information
4. **Password Setup**: Complete account setup

### SSO Integration Points

- **Pre-SSO Check**: Use `/api/auth/check-availability` to determine if user exists
- **Post-SSO Creation**: Use `/api/auth/create-user` if user doesn't exist
- **Contact Verification**: Use `/api/auth/verify-contact` to verify user's contact info
- **Account Completion**: Use `/api/auth/complete-signup` to set password

## Other Authentication Endpoints

### Sign In
**Endpoint:** `POST /api/auth/sign-in`

**Request Body:**
```json
{
    "email": "john.doe@example.com",
    "password": "securepassword123"
}
```

OR

```json
{
    "mobile_number": "+1234567890",
    "password": "securepassword123"
}
```

### Sign Out
**Endpoint:** `POST /api/auth/sign-out`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "refresh_token": "jwt_refresh_token"
}
```

### Individual Verification (Legacy)
**Endpoint:** `POST /api/auth/verify-email`

**Request Body:**
```json
{
    "email": "john.doe@example.com",
    "code": "123456"
}
```

**Endpoint:** `POST /api/auth/verify-mobile`

**Request Body:**
```json
{
    "mobile_number": "+1234567890",
    "otp": "123456"
}
```

### Forgot Password
**Endpoint:** `POST /api/auth/forgot-password`

**Request Body:**
```json
{
    "email": "john.doe@example.com"
}
```

### Reset Password
**Endpoint:** `POST /api/auth/reset-password`

**Request Body:**
```json
{
    "token": "reset_token_from_email",
    "new_password": "newsecurepassword123",
    "confirm_password": "newsecurepassword123"
}
```

## Profile Management Endpoints

### 1. Get/Update Profile
**GET/PUT** `/api/profile/`

**Headers:** `Authorization: Bearer <access_token>`

**GET Response:**
```json
{
    "id": 1,
    "username": "abc123def456",
    "email": "john.doe@example.com",
    "mobile_number": "+1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "is_email_verified": true,
    "is_mobile_verified": true,
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z",
    "last_active": "2024-01-01T00:00:00Z",
    "profile": {
        "id": 1,
        "user": 1,
        "bio": "Software Engineer with 5 years of experience",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "profile_picture": null,
        "website": "https://johndoe.com",
        "linkedin": "https://linkedin.com/in/johndoe",
        "github": "https://github.com/johndoe",
        "twitter": "https://twitter.com/johndoe",
        "country": "United States",
        "state": "California",
        "city": "San Francisco"
    },
    "education": [...],
    "work_experience": [...],
    "skills": [...],
    "interests": [...],
    "projects": [...],
    "resumes": [...]
}
```

### 2. Education Management
**GET** `/api/profile/education/` - List all education records
**POST** `/api/profile/education/` - Create new education record
**GET** `/api/profile/education/{id}/` - Get specific education record
**PUT** `/api/profile/education/{id}/` - Update education record
**DELETE** `/api/profile/education/{id}/` - Delete education record

**Education Request Body:**
```json
{
    "institution": "Stanford University",
    "degree": "Bachelor of Science",
    "field_of_study": "Computer Science",
    "start_date": "2010-09-01",
    "end_date": "2014-06-01",
    "is_current": false,
    "grade": "3.8/4.0",
    "description": "Focused on software engineering and algorithms"
}
```

### 3. Work Experience Management
**GET** `/api/profile/work-experience/` - List all work experience records
**POST** `/api/profile/work-experience/` - Create new work experience record
**GET** `/api/profile/work-experience/{id}/` - Get specific work experience record
**PUT** `/api/profile/work-experience/{id}/` - Update work experience record
**DELETE** `/api/profile/work-experience/{id}/` - Delete work experience record

**Work Experience Request Body:**
```json
{
    "company": "Google",
    "position": "Software Engineer",
    "location": "Mountain View, CA",
    "start_date": "2014-07-01",
    "end_date": "2020-12-31",
    "is_current": false,
    "description": "Developed scalable web applications using Python and JavaScript"
}
```

### 4. Skills Management
**GET** `/api/profile/skills/` - List all skills
**POST** `/api/profile/skills/` - Create new skill
**GET** `/api/profile/skills/{id}/` - Get specific skill
**PUT** `/api/profile/skills/{id}/` - Update skill
**DELETE** `/api/profile/skills/{id}/` - Delete skill

**Skill Request Body:**
```json
{
    "name": "Python",
    "proficiency_level": "expert"
}
```

**Proficiency Levels:** beginner, intermediate, advanced, expert

### 5. Interests Management
**GET** `/api/profile/interests/` - List all interests
**POST** `/api/profile/interests/` - Create new interest
**GET** `/api/profile/interests/{id}/` - Get specific interest
**PUT** `/api/profile/interests/{id}/` - Update interest
**DELETE** `/api/profile/interests/{id}/` - Delete interest

**Interest Request Body:**
```json
{
    "name": "Machine Learning",
    "description": "Interested in AI and ML applications"
}
```

### 6. Projects Management
**GET** `/api/profile/projects/` - List all projects
**POST** `/api/profile/projects/` - Create new project
**GET** `/api/profile/projects/{id}/` - Get specific project
**PUT** `/api/profile/projects/{id}/` - Update project
**DELETE** `/api/profile/projects/{id}/` - Delete project

**Project Request Body:**
```json
{
    "title": "E-commerce Platform",
    "description": "A full-stack e-commerce platform built with Django and React",
    "technologies_used": "Django, React, PostgreSQL, Redis",
    "project_url": "https://myproject.com",
    "github_url": "https://github.com/johndoe/ecommerce",
    "start_date": "2023-01-01",
    "end_date": "2023-06-01",
    "is_current": false
}
```

### 7. Resume Management
**GET** `/api/profile/resumes/` - List all resumes
**POST** `/api/profile/resumes/` - Create new resume
**GET** `/api/profile/resumes/{id}/` - Get specific resume
**PUT** `/api/profile/resumes/{id}/` - Update resume
**DELETE** `/api/profile/resumes/{id}/` - Delete resume

**Resume Request Body:**
```json
{
    "title": "Software Engineer Resume",
    "file": "<file_upload>",
    "is_primary": true,
    "description": "Updated resume for software engineering positions"
}
```

## Token Types

1. **bearer**: JWT access tokens for API authentication
2. **email_verification**: OTP codes sent via email for email verification (6-digit code)
3. **otp_verification**: OTP codes sent via SMS for mobile verification (6-digit code)
4. **forgot_password**: Tokens sent via email for password reset

## Error Responses

All endpoints return consistent error responses:

```json
{
    "error": "Error message description"
}
```

Common HTTP status codes:
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Internal Server Error

## Security Features

1. **Password Validation**: Minimum 8 characters
2. **Token Expiration**: Configurable expiration times
3. **JWT Authentication**: Secure token-based authentication
4. **Email Verification**: Required for full account access
5. **Mobile Verification**: OTP-based verification
6. **Rate Limiting**: Protection against abuse
7. **Input Validation**: Comprehensive validation on all inputs

## Configuration

Update your Django settings:

```python
# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "your-smtp-host"
EMAIL_PORT = 587
EMAIL_HOST_USER = "your-email@domain.com"
EMAIL_HOST_PASSWORD = "your-email-password"
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "noreply@yourdomain.com"

# Site settings
SITE_URL = "https://yourdomain.com"
SITE_NAME = "Your Site Name"

# JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
```

## SMS Integration

For production, integrate with an SMS service like Twilio:

```python
# In palenso/utils/auth_utils.py
from twilio.rest import Client

def send_mobile_otp(user, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=f"Your verification code is: {otp}. Valid for 10 minutes.",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=user.mobile_number
    )
```

## Migration

Run the following commands to set up the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Testing

Test the API endpoints using tools like Postman or curl:

```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/sign-up/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:8000/api/auth/sign-in/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

## Flow Comparison

### Traditional Flow
1. Check availability → Create user → Send verification → Verify → Complete signup

### SSO Flow
1. Check availability → SSO redirect → Create user (if needed) → Verify contact → Complete signup

## Notes

1. **User States:**
   - After Step 2: User is created but `is_active=False`
   - After Step 4: User has verified contact but still `is_active=False`
   - After Step 5: User is activated with `is_active=True`

2. **Verification Requirements:**
   - Both email and mobile must be verified before completing signup
   - Verification codes expire after 10 minutes
   - Single endpoint for verifying both email and mobile

3. **SSO Compatibility:**
   - Availability check before SSO redirect
   - User creation after SSO authentication
   - Contact verification for account security
   - Password setup for local authentication

4. **Security:**
   - Passwords must be at least 8 characters long
   - JWT tokens are used for authentication
   - Refresh tokens can be blacklisted on sign out
   - Users remain inactive until complete verification

5. **Profile Creation:**
   - A user profile is automatically created when user is created
   - The profile can be updated through separate profile endpoints 