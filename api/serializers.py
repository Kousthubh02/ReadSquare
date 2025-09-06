from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import CustomUser, OTPVerification
from utils.email_utils import send_otp_email


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration - creates user and sends email verification OTP
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'username', 'first_name', 'last_name', 
            'phone_number', 'date_of_birth', 'password', 'confirm_password'
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        
        # Create user but don't verify until email is verified
        user = CustomUser.objects.create_user(
            **validated_data,
            is_verified=False,
            is_active=True  # User can login but should verify email
        )
        
        # Create and send email verification OTP
        self._send_email_verification(user)
        
        return user
    
    def _send_email_verification(self, user):
        """Send email verification OTP"""
        # Delete any existing unused OTPs
        OTPVerification.objects.filter(
            email=user.email,
            otp_type='email_verification',
            is_used=False
        ).delete()
        
        # Create new OTP
        otp_obj = OTPVerification.objects.create(
            user=user,
            email=user.email,
            otp_type='email_verification'
        )
        
        # Send OTP email
        send_otp_email(
            email=user.email,
            otp=otp_obj.otp,
            otp_type='email_verification',
            user_name=user.first_name
        )


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for regular user login using email and password
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # First try to find user by email
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user_obj = User.objects.get(email=email)
                
                # Then authenticate using the username
                user = authenticate(request=self.context.get('request'),
                                  username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
            except Exception as e:
                # Log the exception for debugging
                print(f"Authentication error: {e}")
                user = None
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer to verify email using OTP
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        
        try:
            otp_obj = OTPVerification.objects.get(
                email=email,
                otp=otp,
                otp_type='email_verification'
            )
            
            if not otp_obj.is_valid():
                raise serializers.ValidationError("OTP has expired or is invalid")
            
            attrs['otp_obj'] = otp_obj
            attrs['user'] = otp_obj.user
            return attrs
            
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")

    def save(self):
        otp_obj = self.validated_data['otp_obj']
        user = self.validated_data['user']
        
        # Mark email as verified
        user.is_verified = True
        user.save()
        
        # Mark OTP as used
        otp_obj.mark_as_used()
        
        return user


class ResendEmailVerificationSerializer(serializers.Serializer):
    """
    Serializer to resend email verification OTP
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value, is_active=True)
            if user.is_verified:
                raise serializers.ValidationError("Email is already verified")
            return value
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address")

    def create(self, validated_data):
        email = validated_data['email']
        user = CustomUser.objects.get(email=email)
        
        # Delete any existing unused OTPs
        OTPVerification.objects.filter(
            email=email,
            otp_type='email_verification',
            is_used=False
        ).delete()
        
        # Create new OTP
        otp_obj = OTPVerification.objects.create(
            user=user,
            email=email,
            otp_type='email_verification'
        )
        
        # Send OTP email
        send_otp_email(
            email=email,
            otp=otp_obj.otp,
            otp_type='email_verification',
            user_name=user.first_name
        )
        
        return {'email': email, 'message': 'Email verification OTP sent successfully'}


class InitiateForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer to initiate forgot password process - sends OTP to email
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value, is_active=True)
            if not user.is_verified:
                raise serializers.ValidationError("Please verify your email first")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        user = CustomUser.objects.get(email=email)
        
        # Delete any existing unused password reset OTPs
        OTPVerification.objects.filter(
            email=email,
            otp_type='password_reset',
            is_used=False
        ).delete()
        
        # Create new OTP
        otp_obj = OTPVerification.objects.create(
            user=user,
            email=email,
            otp_type='password_reset'
        )
        
        # Send OTP email
        send_otp_email(
            email=email,
            otp=otp_obj.otp,
            otp_type='password_reset',
            user_name=user.first_name
        )
        
        return {'email': email, 'message': 'Password reset OTP sent to your email'}


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer to reset password using OTP
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        email = attrs.get('email')
        otp = attrs.get('otp')
        
        try:
            otp_obj = OTPVerification.objects.get(
                email=email,
                otp=otp,
                otp_type='password_reset'
            )
            
            if not otp_obj.is_valid():
                raise serializers.ValidationError("OTP has expired or is invalid")
            
            attrs['otp_obj'] = otp_obj
            attrs['user'] = otp_obj.user
            return attrs
            
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")

    def save(self):
        otp_obj = self.validated_data['otp_obj']
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        
        # Reset password
        user.set_password(new_password)
        user.save()
        
        # Mark OTP as used
        otp_obj.mark_as_used()
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password when logged in
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details
    """
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'is_verified', 'full_name', 
            'date_joined', 'last_login', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'is_verified', 'date_joined', 'last_login', 'created_at', 'updated_at')


    
