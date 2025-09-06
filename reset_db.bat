@echo off
echo Resetting Django database and migrations...
echo.

REM Delete SQLite database
if exist db.sqlite3 (
    del db.sqlite3
    echo ✓ Deleted db.sqlite3
) else (
    echo ! db.sqlite3 not found
)

REM Delete migration files (keep __init__.py)
if exist api\migrations\0001_initial.py del api\migrations\0001_initial.py
if exist api\migrations\0002_customuser_otpverification.py del api\migrations\0002_customuser_otpverification.py

REM Delete migration cache
if exist api\migrations\__pycache__ (
    rmdir /s /q api\migrations\__pycache__
    echo ✓ Deleted migration cache
)

echo ✓ Cleaned up old migrations
echo.

REM Create fresh migrations
echo Creating new migrations...
python manage.py makemigrations api
if %errorlevel% neq 0 (
    echo ❌ Failed to create migrations
    pause
    exit /b 1
)

echo.
echo Applying migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ❌ Failed to apply migrations
    pause
    exit /b 1
)

echo.
echo ✅ Database reset complete!
echo.
echo Next steps:
echo 1. Create superuser: python manage.py createsuperuser
echo 2. Run server: python manage.py runserver
echo.
pause
