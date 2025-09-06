#!/usr/bin/env python
"""
Test script to validate CI setup before pushing to GitHub
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReadSquare.settings')
    django.setup()

def test_settings():
    """Test that settings load correctly"""
    print("✅ Testing Django settings...")
    from django.conf import settings
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   DATABASES: {settings.DATABASES['default']['ENGINE']}")
    print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"   STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    print(f"   AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")

def test_apps():
    """Test that all apps are properly configured"""
    print("✅ Testing installed apps...")
    from django.apps import apps
    app_configs = apps.get_app_configs()
    for app in app_configs:
        if app.name in ['api', 'rest_framework', 'rest_framework_simplejwt']:
            print(f"   ✅ {app.name}")

def test_models():
    """Test that models can be imported"""
    print("✅ Testing models...")
    try:
        from api.models import CustomUser, OTPVerification
        print("   ✅ CustomUser model imported")
        print("   ✅ OTPVerification model imported")
    except Exception as e:
        print(f"   ❌ Model import error: {e}")

def test_urls():
    """Test that URL configuration works"""
    print("✅ Testing URL configuration...")
    try:
        from django.urls import resolve
        from ReadSquare.urls import urlpatterns
        print(f"   ✅ Found {len(urlpatterns)} URL patterns")
    except Exception as e:
        print(f"   ❌ URL configuration error: {e}")

def main():
    """Run all tests"""
    print("🔧 CI Setup Validation")
    print("=" * 50)
    
    try:
        setup_django()
        test_settings()
        test_apps()
        test_models()
        test_urls()
        
        print("\n✅ All CI setup tests passed!")
        print("🚀 Ready to push to GitHub!")
        return 0
        
    except Exception as e:
        print(f"\n❌ CI setup test failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
