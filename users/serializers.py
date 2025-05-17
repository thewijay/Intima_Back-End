from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 'gender_other',
            'height_cm', 'weight_kg', 'marital_status', 'sexually_active',
            'menstrual_cycle', 'medical_conditions', 'profile_completed'
        ]

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email  # optional custom claim
        return token

    def validate(self, attrs):
        attrs['username'] = attrs.get('email')  # map email to username for auth
        return super().validate(attrs)
