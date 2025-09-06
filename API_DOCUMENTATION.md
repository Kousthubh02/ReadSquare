# ReadSquare API Endpoints

## Authentication Endpoints

### User Registration
- **POST** `/api/auth/register/`
- **Body**: 
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01",
    "password": "securepassword",
    "confirm_password": "securepassword"
  }
  ```

### User Login
- **POST** `/api/auth/login/`
- **Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```

### User Logout
- **POST** `/api/auth/logout/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: 
  ```json
  {
    "refresh_token": "refresh_token_here"
  }
  ```

### Refresh Token
- **POST** `/api/auth/refresh-token/`
- **Body**: 
  ```json
  {
    "refresh_token": "refresh_token_here"
  }
  ```

## Email Verification Endpoints

### Verify Email
- **POST** `/api/auth/verify-email/`
- **Body**: 
  ```json
  {
    "email": "user@example.com",
    "otp": "123456"
  }
  ```

### Resend Verification Email
- **POST** `/api/auth/resend-verification/`
- **Body**: 
  ```json
  {
    "email": "user@example.com"
  }
  ```

### Check Verification Status
- **GET** `/api/auth/check-verification-status/`
- **Headers**: `Authorization: Bearer <access_token>`

## Password Management Endpoints

### Forgot Password
- **POST** `/api/auth/forgot-password/`
- **Body**: 
  ```json
  {
    "email": "user@example.com"
  }
  ```

### Reset Password
- **POST** `/api/auth/reset-password/`
- **Body**: 
  ```json
  {
    "email": "user@example.com",
    "otp": "123456",
    "new_password": "newsecurepassword",
    "confirm_password": "newsecurepassword"
  }
  ```

### Change Password (Authenticated)
- **POST** `/api/auth/change-password/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body**: 
  ```json
  {
    "old_password": "currentpassword",
    "new_password": "newsecurepassword",
    "confirm_new_password": "newsecurepassword"
  }
  ```

## User Profile Endpoints

### Get/Update User Profile
- **GET/PATCH** `/api/user/profile/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Body** (for PATCH): 
  ```json
  {
    "first_name": "Updated Name",
    "phone_number": "+1234567890"
  }
  ```

### Get Current User
- **GET** `/api/user/me/`
- **Headers**: `Authorization: Bearer <access_token>`

## Admin Endpoints

### Get All Users (Admin Only)
- **GET** `/api/admin/users/`
- **Headers**: `Authorization: Bearer <admin_access_token>`

## Response Format

### Success Response
```json
{
  "message": "Operation successful",
  "data": {},
  "status": "success"
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": {},
  "status": "error"
}
```

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## OTP Expiration

- OTP codes expire after 10 minutes
- Only one active OTP per email/type at a time
- Used OTPs cannot be reused
