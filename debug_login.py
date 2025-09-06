#!/usr/bin/env python
"""
Debug script to test the login functionality
"""
import os

import django
from django.contrib.auth import authenticate, get_user_model
from django.test import Client

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ReadSquare.settings")
django.setup()


def test_login_debug():
    """Debug the login issue"""
    User = get_user_model()

    # Create test user
    print("Creating test user...")
    user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123", is_verified=True)
    print(f"User created: {user.username}, email: {user.email}")

    # Test authenticate directly
    print("\nTesting authenticate directly...")
    auth_user = authenticate(username="testuser", password="testpass123")
    print(f"Authenticate with username: {auth_user}")

    auth_user_email = authenticate(username="test@example.com", password="testpass123")
    print(f"Authenticate with email: {auth_user_email}")

    # Test via API client
    print("\nTesting via API client...")
    client = Client()
    login_data = {"email": "test@example.com", "password": "testpass123"}

    response = client.post("/api/auth/login/", login_data, content_type="application/json")
    print(f"API response status: {response.status_code}")
    print(f"API response content: {response.content.decode()}")

    # Cleanup
    user.delete()
    print("\nTest user deleted")


if __name__ == "__main__":
    test_login_debug()
