from rest_framework import serializers
from auth_app.models import User
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering new users."""
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'repeated_password',
            'type',
        ]
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    def create(self, validated_data):
        """Create a new user with a hashed password.

        Args:
            validated_data (dict): The validated registration data,
                including ``password`` and ``repeated_password``.

        Returns:
            User: The newly created and saved user instance.
        """
        password = validated_data.pop('password')
        validated_data.pop('repeated_password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def validate(self, attrs):
        """Check that the password and repeated password match.

        Args:
            attrs (dict): The deserialized input data, including
                ``password`` and ``repeated_password``.

        Returns:
            dict: The unchanged input data if both passwords match.

        Raises:
            serializers.ValidationError: If the passwords do not match.
        """
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({
                'repeated_password': 'Passwords do not match.'
            })

        return attrs

    def validate_email(self, value):
        """Make sure the email address is not already registered.

        Args:
            value (str): The email address to check.

        Returns:
            str: The email address if no user has it yet.

        Raises:
            serializers.ValidationError: If a user with this email
                already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Email already exists.'
            )

        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for login users."""
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Authenticate the user with the given username and password.

        Args:
            attrs (dict): The deserialized input data with ``username``
                and ``password``.

        Returns:
            dict: The input data with the authenticated user added under
                the ``user`` key.

        Raises:
            serializers.ValidationError: If the username or password is
                invalid.
        """
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                {"error": "Invalid username or password."}
            )

        attrs["user"] = user
        return attrs
