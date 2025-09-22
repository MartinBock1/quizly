from rest_framework import serializers
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    This serializer is used to handle the creation of new user accounts.
    It includes fields for username, email, password field.
    It provides that the email address is unique.
    """

    class Meta:
        """
        Meta class to specify the serializer's options.
        """
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def validate_email(self, value):
        """
        Check if the email is already in use.

        Args:
            value (str): The email address to validate.

        Raises:
            serializers.ValidationError: If a user with the given email already exists.

        Returns:
            str: The validated email address.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self):
        """
        Create and save a new User instance.

        This method overrides the default save() method to handle password hashing.
        It creates a new user with the validated email and username, sets the
        password securely, and saves the new user to the database.

        Returns:
            User: The newly created user account instance.
        """        
        pw = self.validated_data['password']        
        account = User(
            email=self.validated_data['email'],
            username=self.validated_data['username']
        )
        account.set_password(pw)
        account.save()
        
        return account
