from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data.get('email')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
