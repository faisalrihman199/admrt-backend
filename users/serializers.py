from rest_framework import serializers
from .models import (
    SpaceHost,
    Advertiser,
    AdvertiserProduct,
    Topic,
    SocialMedia,
    Portfolio,
    AdSpaceForSpaceHost,
)
from core.models import User

# Profile Serializers
class AdSpaceForSpaceHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdSpaceForSpaceHost
        fields = ['id', 'space_type', 'file', 'url']


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ['id', 'social_media', 'url']


# class ProductImageUploadSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductImageUploadFragment
#         fields = ['id', 'file']


class ProductSerializer(serializers.ModelSerializer):
    # images = ProductImageUploadSerializer(many=True, read_only=True)
    class Meta:
        model = AdvertiserProduct
        fields = ['id', 'name', 'description', 'image1', 'image2', 'image3',"productType"]


class AdvertiserSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    socials = SocialMediaSerializer(many=True, read_only=True)
    joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    id = serializers.IntegerField(source='user.id', read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    user_role = serializers.CharField(source='user.user_role', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Advertiser
        fields = ['id', 'full_name', 'profile_image', 'banner_image', 'description', 'location', 'website', 'is_admin', 'joined', 'products', 'socials', 'user_role', 'user']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'title']


# class PortfolioImageUploadSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PortfolioImageUploadFragment
#         fields = ['id', 'file']
        

class PortfolioSerializer(serializers.ModelSerializer):
    # images = PortfolioImageUploadSerializer(many=True, read_only=True)
    class Meta:
        model = Portfolio
        fields = ['id', 'title', 'description', 'image1', 'image2', 'image3', 'youtube_url']


# class LanguageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Language
#         fields = ['id', 'language']


class SpaceHostSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    # languages = LanguageSerializer(many=True, read_only=True)
    portfolios = PortfolioSerializer(many=True, read_only=True)
    socials = SocialMediaSerializer(many=True, read_only=True)
    ad_spaces = AdSpaceForSpaceHostSerializer(many=True, read_only=True)
    joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    id = serializers.IntegerField(source='user.id', read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    user_role = serializers.CharField(source='user.user_role', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = SpaceHost
        fields = ['id', 'full_name', 'profile_image', 'banner_image', 'description', 'location', 'website', 'is_admin', 'joined', 'long_term_service_availability', 'topics', 'languages', 'portfolios', 'socials', 'ad_spaces', 'user_role', 'user']


class AdvertiserProductCountSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'product_count']