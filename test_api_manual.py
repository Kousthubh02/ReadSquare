#!/usr/bin/env python
"""
Manual API Testing Script
Run this script to test API endpoints manually during development
"""

import sys
from urllib.parse import urljoin

import requests

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = urljoin(BASE_URL, "/api/")


class APITester:
    def __init__(self, base_url=API_BASE):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None

    def make_request(self, method, endpoint, data=None, auth=True):
        """Make HTTP request to API endpoint"""
        url = urljoin(self.base_url, endpoint)
        headers = {"Content-Type": "application/json"}

        if auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        try:
            response = self.session.request(method=method, url=url, json=data, headers=headers)
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def test_user_registration(self):
        """Test user registration endpoint"""
        print("\n🔄 Testing User Registration...")

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "confirm_password": "testpass123",
        }

        response = self.make_request("POST", "auth/register/", data, auth=False)

        if response:
            if response.status_code == 201:
                print("✅ User registration successful")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ User registration failed: {response.status_code}")
                print(f"   Error: {response.text}")

        return response

    def test_user_login(self):
        """Test user login endpoint"""
        print("\n🔄 Testing User Login...")

        data = {"email": "test@example.com", "password": "testpass123"}

        response = self.make_request("POST", "auth/login/", data, auth=False)

        if response:
            if response.status_code == 200:
                print("✅ User login successful")
                result = response.json()
                if "tokens" in result:
                    self.access_token = result["tokens"]["access"]
                    print("   🔑 JWT token obtained")
                print(f"   Response: {result}")
            else:
                print(f"❌ User login failed: {response.status_code}")
                print(f"   Error: {response.text}")

        return response

    def test_user_profile(self):
        """Test user profile endpoint"""
        print("\n🔄 Testing User Profile...")

        if not self.access_token:
            print("❌ No access token available. Login first.")
            return None

        response = self.make_request("GET", "user/me/")

        if response:
            if response.status_code == 200:
                print("✅ User profile retrieved successfully")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ User profile failed: {response.status_code}")
                print(f"   Error: {response.text}")

        return response

    def test_resend_verification(self):
        """Test resend email verification endpoint"""
        print("\n🔄 Testing Resend Email Verification...")

        data = {"email": "test@example.com"}

        response = self.make_request("POST", "auth/resend-verification/", data, auth=False)

        if response:
            if response.status_code == 200:
                print("✅ Resend verification successful")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Resend verification failed: {response.status_code}")
                print(f"   Error: {response.text}")

        return response

    def test_forgot_password(self):
        """Test forgot password endpoint"""
        print("\n🔄 Testing Forgot Password...")

        data = {"email": "test@example.com"}

        response = self.make_request("POST", "auth/forgot-password/", data, auth=False)

        if response:
            if response.status_code == 200:
                print("✅ Forgot password initiated successfully")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Forgot password failed: {response.status_code}")
                print(f"   Error: {response.text}")

        return response

    def test_all_endpoints(self):
        """Run all API tests"""
        print("🚀 Starting API Tests...")
        print(f"   Base URL: {self.base_url}")

        # Test registration
        self.test_user_registration()

        # Test login
        self.test_user_login()

        # Test authenticated endpoints
        if self.access_token:
            self.test_user_profile()

        # Test other endpoints
        self.test_resend_verification()
        self.test_forgot_password()

        print("\n🏁 API Tests Complete!")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        if not base_url.endswith("/"):
            base_url += "/"
        api_base = urljoin(base_url, "api/")
    else:
        api_base = API_BASE

    print("🧪 API Testing Tool")
    print(f"   Target: {api_base}")
    print("=" * 50)

    tester = APITester(api_base)

    try:
        tester.test_all_endpoints()
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
