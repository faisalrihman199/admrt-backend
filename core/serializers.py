from typing import Any, Dict
from django.conf import settings
# from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
# from django.utils.crypto import get_random_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
# from djoser.serializers import PasswordResetSerializer as DjoserPasswordResetSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as BaseTokenObtainPairSerializer

from core.models import User
from core.utils import get_profile_image_url
from users.models import SpaceHost, Advertiser
from .models import AffiliateLink


class UserCreateSerializer(BaseUserCreateSerializer):
    username = serializers.CharField(read_only=True)
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'email', 'password', 'full_name', 'phone', 'country', 'birthday', 'user_role']

    def create(self, validated_data):
        user = super().create(validated_data)
        user_role = validated_data.get('user_role')
        
        profile_class = None
        if user_role == settings.K_SPACE_HOST_ID:
            profile_class = SpaceHost
        elif user_role == settings.K_ADVERTISER_ID:
            profile_class = Advertiser
        if profile_class is not None:
            profile_class.objects.create(user=user)
        
        return user


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'full_name', 'phone', 'country', 'birthday', 'user_role']
        
        
class UserDetailSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id",'full_name', 'email', 'phone', 'country', 'birthday', 'user_role', 'last_seen', 'profile_image']
        read_only_fields = ['email', 'user_role']

    def get_profile_image(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            return obj.profile.profile_image.url  # Return the URL of the profile image
        return None  # Return None if no profile image is available

        
        
class UserPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'phone', 'country', 'birthday']
        

class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        image_url = None
        is_admin = None
        if hasattr(user, 'profile'):
            image_url = get_profile_image_url(user.profile.profile_image)
            is_admin = user.profile.is_admin
        token['id'] = user.id
        token['email'] = user.email
        token['username'] = user.username
        token['full_name'] = user.full_name
        token['profile_image'] = image_url
        token['is_admin'] = is_admin
        token['user_role'] = user.user_role
        return token
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        image_url = None
        is_admin = None
        if hasattr(self.user, 'profile'):
            image_url = get_profile_image_url(self.user.profile.profile_image)
            is_admin = self.user.profile.is_admin
        data['user'] = {
            "id": self.user.id,
            "email": self.user.email,
            "username": self.user.username,
            "full_name": self.user.full_name,
            "profile_image": image_url,
            "is_admin": is_admin,
            "phone": self.user.phone,
            "country": self.user.country,
            "user_role": self.user.user_role
        }
        return data
    
    
# class PasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         user = User.objects.filter(email=value).first()
#         if not user:
#             raise serializers.ValidationError(_("No user is associated with this email address."))
#         return value

#     def save(self):
#         user = User.objects.get(email=self.validated_data['email'])
#         user.set_reset_code()

#         # Send the code via email
#         send_mail(
#             'Password reset code',
#             f'Your password reset code is: {user.reset_code}',
#             settings.DEFAULT_FROM_EMAIL,
#             [user.email],
#             fail_silently=False,
#         )


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("No user is associated with this email address.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.set_reset_code()

        # Prepare email context
        context = {
            'reset_code': user.reset_code,
            'site_name': 'AdMrt',
            'full_name': user.full_name,
        }

        # Render the HTML template
        html_content = render_to_string('emails/password_reset.html', context)
        text_content = strip_tags(html_content)

        # Send email
        email = EmailMultiAlternatives(
            subject="Password Reset on AdMrt",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        
class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if not user or not user.validate_reset_code(data['reset_code']):
            raise serializers.ValidationError("Invalid reset code or email.")
        return data

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['new_password'])
        user.clear_reset_code()
        user.save()

class UserCountSerializer(serializers.Serializer):
    period = serializers.CharField()
    data = serializers.DictField()  # Allowing any structure for the data


class AdvertiserProductCountSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'product_count']

class AffiliateLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateLink
        fields = ['url']

    def validate_url(self, value):
        # Check if the URL already exists
        if AffiliateLink.objects.filter(url=value).exists():
            raise serializers.ValidationError("URL already exists")
        return value