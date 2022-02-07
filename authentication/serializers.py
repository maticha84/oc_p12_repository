from rest_framework.serializers import ModelSerializer, ValidationError, CharField
from django.contrib.auth import password_validation
from .models import User


class RegistrationSerializer(ModelSerializer):
    confirm_password = CharField(max_length=128, style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'user_team', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

    def validate_password(self, password):
        password_validation.validate_password(password, self.instance)
        return password

    def save(self):
        """
        to save a user registration --> create a new user objects if all data are validated
        """
        user = User(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            email=self.validated_data['email'],
            user_team=self.validated_data['user_team'],
        )

        password = self.validated_data['password']
        password = self.validate_password(password)
        confirm_password = self.validated_data['confirm_password']

        if password != confirm_password:
            raise ValidationError({'Password': "passwords don't match"})

        if user.user_team == 1:
            user.is_staff = True
        user.set_password(password)
        user.save()
        return user


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'user_team']
