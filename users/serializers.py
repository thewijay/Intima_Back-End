from rest_framework import serializers
from .models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 'gender_other',
            'height_cm', 'weight_kg', 'marital_status', 'sexually_active',
            'menstrual_cycle', 'medical_conditions', 'profile_completed'
        ]
