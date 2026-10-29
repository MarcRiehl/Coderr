#python manage.py test profiles_app.tests.test_profiles

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from profiles_app.models import Profile


User = get_user_model()

