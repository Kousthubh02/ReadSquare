# Django Setup Instructions

## ⚠️ IMPORTANT: Database Migration Required

Since we changed the user model, you'll need to reset your database. Follow these steps:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Delete Existing Database and Migrations
```bash
# Delete the SQLite database
del db.sqlite3

# Delete migration files (keep the __init__.py)
del api\migrations\*.py
# Then recreate __init__.py
echo. > api\migrations\__init__.py
```

### 3. Create New Migrations
```bash
python manage.py makemigrations api
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

## What Was Fixed

✅ **Fixed User Model Conflicts**: 
- Added `AUTH_USER_MODEL = 'api.CustomUser'` to settings
- Removed Django's default User model import
- Updated Customer model to use CustomUser

✅ **JWT Configuration**:
- Added JWT authentication to REST_FRAMEWORK settings
- Added SIMPLE_JWT configuration
- Added 'rest_framework_simplejwt' to INSTALLED_APPS

✅ **Model Organization**:
- Moved CustomUser to top of models.py
- Updated OTP_TYPES to match email_utils.py
- Removed duplicate model definitions

## API Endpoints Available

After setup, you can test these endpoints:
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/verify-email/` - Email verification
- `GET /api/user/me/` - Get current user profile
- And many more (see API_DOCUMENTATION.md)

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Reset database following steps above
3. Test the API endpoints using Postman or similar tool
4. Configure email settings for OTP functionality (SMTP)
