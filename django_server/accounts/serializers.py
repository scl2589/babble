from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer

from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

from .models import User, BabyAccess, Rank, Group, UserBabyRelationship
from babies.serializers import BabySerializer

class CustomRegisterSerializer(RegisterSerializer):
    name = serializers.CharField(
        required=False,
        max_length=50,
    )

    profile_image = serializers.CharField(
        required=False,
        max_length=200,
    )

    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()
        data_dict['name'] = self.validated_data.get('name', '')
        data_dict['profile_image'] = self.validated_data.get('profile_image', '')
        return data_dict

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'profile_image', 'groups', 'visited_babies']

class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = '__all__'

class GroupListSerializer(serializers.ModelSerializer):
    baby = BabySerializer(required=False)
    class Meta:
        model = Group
        fields = '__all__'

class UserBabyRelationshipSerializer(serializers.ModelSerializer):
    baby = BabySerializer(required=False)
    rank = RankSerializer(required=False)
    class Meta:
        model = UserBabyRelationship
        fields = '__all__'