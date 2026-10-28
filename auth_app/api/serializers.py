from rest_framework import serializers
from ..models import User
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
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
        password = validated_data.pop('password') #Passwort wird aus validated_data entfernt
        validated_data.pop('repeated_password')

        user = User(**validated_data) #verbleibene Dicionary Einträge
        user.set_password(password) #hasht Passwort
        user.save()

        return user

    def validate(self, attrs):
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({
                'repeated_password': 'Passwords do not match.'
            })

        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Email already exists.'
            )

        return value

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
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

