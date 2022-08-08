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


class ProfileViewSetTestCase(APITestCase):
    list_url = reverse("api:profile-list")

    def setUp(self):
        self.username = "kratos"
        self.password = "user12345"
        self.user = Profile.objects.create_user(self.username, self.password)
        self.user.save()
        self.api_creating_testusers()
        self.api_authentication()

    def api_authentication(self):
        # login
        self.client.force_authenticate(self.user)  # or to url /accounts/login/ or use Basic authorization

    def api_creating_testusers(self):
        # Register new users
        for _ in range(10):
            user = Profile.objects.create_user(
                username=f'user{_}',
                password='user12345',
                email=f'testingUser{_}@gmail.com',
                first_name=f'Name{_} Test',
                last_name=f'LastName{_} Test',
            )
            user.save()

    def test_registration(self):
        data = {
            'username': 'TestingUser',
            'email': 'testingUser@gmail.com',
            'first_name': 'Test',
            'last_name': 'Test',
            'password': 'user12345',
        }
        response = self.client.post('/api/profile/', data)

        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.data['first_name'], data['first_name'])
        self.assertEqual(response.data['last_name'], data['last_name'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_profile_list_authenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_list_un_authenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detial(self):
        temp_user = Profile.objects.get(username='user0')

        response = self.client.get(reverse("api:profile-detail", kwargs={'pk': temp_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'], temp_user.pk)
        self.assertEqual(response.data['username'], temp_user.username)
        self.assertEqual(response.data['email'], temp_user.email)
        self.assertEqual(response.data['first_name'], temp_user.first_name)
        self.assertEqual(response.data['last_name'], temp_user.last_name)
        self.assertEqual(response.data['bio'], temp_user.bio)
        self.assertEqual(response.data['slug'], temp_user.slug)
        self.assertEqual(response.data['is_staff'], temp_user.is_staff)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_post_create_get_and_ordering(self):
        user_pool = Profile.objects.all()[:3]
        data = [{
            'title': user.username,
            'content': f'content by {user.username}',
        } for user in user_pool]
        for i in range(len(user_pool)):
            self.client.force_authenticate(user_pool[i])
            response = self.client.post(reverse("api:post-list"), data[i])
            self.assertEqual(response.data['title'], data[i]['title'])
            self.assertEqual(response.data['content'], data[i]['content'])
            self.assertEqual(response.data['author']['username'], user_pool[i].username)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            url = response.data['id']
            response = self.client.get(url)
            self.assertEqual(response.data['title'], data[i]['title'])
            self.assertEqual(response.data['content'], data[i]['content'])
            self.assertEqual(response.data['author']['username'], user_pool[i].username)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.post(reverse("api:post-list"), data[2])
        self.client.post(reverse("api:post-list"), data[2])

        self.client.force_authenticate(user_pool[1])
        self.client.post(reverse("api:post-list"), data[1])

        response = self.client.get(f'{reverse("api:profile-list")}?ordering=posts')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['username'], 'user1')
        self.assertEqual(response.data[1]['username'], 'user0')

        # View a list of other users' posts sorted by creation date, fresh first.
        response = self.client.get(reverse("api:post-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['author']['username'], 'user0')

    def test_sub_un_sub_and_feed(self):
        # Authorized users subscribe and unsubscribe to other users' posts.

        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("api:profile-sub-unsub", kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("api:profile-sub-unsub", kwargs={'pk': Profile.objects.get(username='user2').pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for user in Profile.objects.all()[4:7]:
            self.client.force_authenticate(user)
            for i in range(6):
                self.client.post(reverse("api:post-list"), {
                    'title': f'title of {user.username}',
                    'content': f'cotent of {user.username}'
                })

        self.client.get(reverse("api:profile-sub-unsub", kwargs={'pk': Profile.objects.get(username='user4').pk}))
        self.client.get(reverse("api:profile-sub-unsub", kwargs={'pk': Profile.objects.get(username='user5').pk}))

        # For authorized users to form a feed from the posts of users to which a subscription has been made. New
        # posts of users get into the feed after the subscription is completed. Sort by post creation date,
        # fresh first. The list of posts is given in pages of 10 pcs.
        response = self.client.get(reverse("api:feed-list"))
        for post in response.data['results']:
            if post['author']['username'] == 'user6':
                self.assertRaises(BaseException)  # we didn't subscribe to this user

        self.assertEqual(len(response.data['results']), 10)
        self.assertGreater(response.data['count'], 10)
