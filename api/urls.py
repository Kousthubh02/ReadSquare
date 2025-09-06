from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Authentication URLs
    path('auth/register/', views.UserRegistrationView.as_view(), name='user_register'),
    path('auth/login/', views.UserLoginView.as_view(), name='user_login'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('auth/refresh-token/', views.RefreshTokenView.as_view(), name='refresh_token'),
    
    # Email Verification URLs
    path('auth/verify-email/', views.EmailVerificationView.as_view(), name='verify_email'),
    path('auth/resend-verification/', views.ResendEmailVerificationView.as_view(), name='resend_verification'),
    path('auth/check-verification-status/', views.check_email_verification_status, name='check_verification_status'),
    
    # Password Management URLs
    path('auth/forgot-password/', views.InitiateForgotPasswordView.as_view(), name='forgot_password'),
    path('auth/reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # User Profile URLs
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('user/me/', views.get_user_profile, name='get_user_profile'),
    
    # Admin URLs
    path('admin/users/', views.get_all_users, name='get_all_users'),
]
