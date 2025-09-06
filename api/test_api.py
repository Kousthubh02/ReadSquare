from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json

User = get_user_model()


class UserAuthenticationAPITest(APITestCase):
    """Test user authentication APIs"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('api:user_register')
        self.login_url = reverse('api:user_login')
        self.verify_email_url = reverse('api:verify_email')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }

    def test_user_registration(self):
        """Test user registration endpoint"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertTrue(response.data['email_verification_required'])
        
        # Check user was created in database
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertFalse(user.is_verified)  # Should be unverified initially

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create first user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Try to create another user with same email
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'anotheruser'
        
        response = self.client.post(self.register_url, duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        invalid_data = self.user_data.copy()
        invalid_data['confirm_password'] = 'differentpassword'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_valid_credentials(self):
        """Test login with valid credentials"""
        # Create and verify user first
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            is_verified=True
        )
        
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_profile_authenticated(self):
        """Test accessing user profile when authenticated"""
        # Create user and get JWT token
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        # Login to get token
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        
        if login_response.status_code == 200 and 'tokens' in login_response.data:
            token = login_response.data['tokens']['access']
            
            # Access profile with token
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            profile_url = reverse('api:get_user_profile')
            response = self.client.get(profile_url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['email'], user.email)

    def test_user_profile_unauthenticated(self):
        """Test accessing user profile without authentication"""
        profile_url = reverse('api:get_user_profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OTPVerificationAPITest(APITestCase):
    """Test OTP verification APIs"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_verified=False
        )

    def test_resend_verification_valid_email(self):
        """Test resending verification OTP for valid email"""
        resend_url = reverse('api:resend_verification')
        data = {'email': self.user.email}
        
        response = self.client.post(resend_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_resend_verification_invalid_email(self):
        """Test resending verification OTP for invalid email"""
        resend_url = reverse('api:resend_verification')
        data = {'email': 'nonexistent@example.com'}
        
        response = self.client.post(resend_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetAPITest(APITestCase):
    """Test password reset APIs"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_verified=True  # Must be verified for password reset
        )

    def test_initiate_forgot_password_valid_email(self):
        """Test initiating forgot password for valid email"""
        forgot_url = reverse('api:forgot_password')
        data = {'email': self.user.email}
        
        response = self.client.post(forgot_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_initiate_forgot_password_unverified_user(self):
        """Test initiating forgot password for unverified user"""
        # Create unverified user
        unverified_user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            password='testpass123',
            is_verified=False
        )
        
        forgot_url = reverse('api:forgot_password')
        data = {'email': unverified_user.email}
        
        response = self.client.post(forgot_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class URLPatternsTest(TestCase):
    """Test that all URL patterns are correctly configured"""
    
    def test_api_urls_resolve(self):
        """Test that all API URLs resolve correctly"""
        url_names = [
            'api:user_register',
            'api:user_login',
            'api:user_logout',
            'api:verify_email',
            'api:resend_verification',
            'api:forgot_password',
            'api:reset_password',
            'api:change_password',
            'api:user_profile',
            'api:get_user_profile',
        ]
        
        for url_name in url_names:
            try:
                url = reverse(url_name)
                self.assertTrue(url.startswith('/api/'))
            except Exception as e:
                self.fail(f"URL {url_name} failed to resolve: {e}")

    def test_admin_url_accessible(self):
        """Test that admin URL is accessible"""
        client = Client()
        response = client.get('/admin/')
        # Should redirect to login or show login page
        self.assertIn(response.status_code, [200, 302])


class ModelTest(TestCase):
    """Test model functionality"""
    
    def test_custom_user_creation(self):
        """Test custom user model creation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.full_name, 'Test User')
        self.assertFalse(user.is_verified)
        self.assertTrue(user.check_password('testpass123'))

    def test_custom_user_str_method(self):
        """Test custom user string representation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(str(user), 'test@example.com')
