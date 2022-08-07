from django.test import TestCase
import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profiles.models import *
from posts.models import *
from .serializers import ProfileSerializer


class RegistrationTestCase(APITestCase):
    pass

class ProfileViewSetTestCase(APITestCase):
    list_url = reverse("api:profile-list")

    def setUp(self):
        self.username = "kratos"
        self.password = "user12345"
        self.user = Profile.objects.create_user(self.username, self.password)
        self.api_authentication()

    def api_authentication(self):
        self.client.force_authenticate(self.user)

    def api_creating_testusers(self):
        for _ in range(10):
            Profile.objects.create_user('user' + str(_), 'user12345')

    def test_registration(self):
        data = {
            'username': 'TestingUser',
            'email': 'testingUser@gmail.com',
            'first_name': 'Test',
            'last_name': 'Test',
            'first_name': 'Test',
            'password': 'user12345',
        }
        response = self.client.post('/api/profile/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_profile_list_authenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_list_un_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detial(self):
        temp_user = Profile.objects.create_user(username='OneMoreUser', password='user12345',
                                                email='oneMoreUser@gmail.com')
        print(self.list_url + f'{temp_user.pk}/')

        response = self.client.get(self.list_url + f'{temp_user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], temp_user.username)
        self.assertEqual(response.data['email'], temp_user.email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


