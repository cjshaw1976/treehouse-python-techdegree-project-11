import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from . import serializers


class TestUserCreate(APITestCase):
    def test_create_user(self):
        client = APIClient()
        response = client.post(reverse('register-user'),
                               data={'username': 'toaster',
                                     'password': 'toaster'},
                               format='json')
        self.assertEqual(response.status_code, 201)


class SetTestCase(APITestCase):
    """Create a test user and import data on dogs."""

    def setUp(self):
        self.testuser = User.objects.create(username='testuser',
                                            password='testuser')
        self.token = Token.objects.create(user=self.testuser)
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )

        with open('pugorugh/static/dog_details.json', 'r') as file:
            data = json.load(file)

            serializer = serializers.DogSerializer(data=data, many=True)
            if serializer.is_valid():
                serializer.save()


class TestInital(SetTestCase):
    """Test inital databse setting"""

    def test_api_can_get_user_pref(self):
        """Test the api can get the user preferences"""
        response = self.client.get('/api/user/preferences/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['age'], 'b,y,a,s')
        self.assertEqual(response.data['gender'], 'm,f')
        self.assertEqual(response.data['size'], 's,m,l,xl')

    def test_api_can_get_first_dog(self):
        """Test the api can get first dog, undecided."""
        response = self.client.get(reverse('api:dog-detail',
                                           kwargs={'pk': -1}
                                           ) + 'undecided/next/')
        self.assertEqual(response.status_code, 200)

    def test_api_can_get_first_liked_dog(self):
        """
        Test the api can get first liked dog.
        Should return 404 as all undecided
        """
        response = self.client.get(reverse('api:dog-detail',
                                           kwargs={'pk': -1}
                                           ) + 'liked/next/')
        self.assertEqual(response.status_code, 404)

    def test_api_can_get_first_disliked_dog(self):
        """
        Test the api can get first disliked dog.
        Should return 404 as all undecided
        """
        response = self.client.get(reverse('api:dog-detail',
                                           kwargs={'pk': -1}
                                           ) + 'disliked/next/')
        self.assertEqual(response.status_code, 404)


class TestUserPref(SetTestCase):
    """Apply UserPref"""

    def test_api_can_put_user_pref(self):
        response = self.client.put(
            '/api/user/preferences/',
            data={'age': 's', 'gender': 'm', 'size': 's'},
            format='json')
        self.assertEqual(response.status_code, 200)


class TestLike(SetTestCase):
    """Test liked, disliked and undecided"""

    def test_liked(self):
        """Like the dog with pk=1"""
        response = self.client.put(reverse('api:dog-detail',
                                           kwargs={'pk': 1}
                                           ) + 'liked/')
        self.assertEqual(response.status_code, 204)
        """Check it shows up in liked"""
        response = self.client.get(reverse('api:dog-detail',
                                           kwargs={'pk': 1}
                                           ) + 'liked/next/')
        self.assertEqual(response.status_code, 200)

    def test_disliked(self):
        """Like the dog with pk=2"""
        response = self.client.put(reverse('api:dog-detail',
                                           kwargs={'pk': 2}
                                           ) + 'disliked/')
        self.assertEqual(response.status_code, 204)
        """Check it shows up in disliked"""
        response = self.client.get(reverse('api:dog-detail',
                                           kwargs={'pk': 2}
                                           ) + 'disliked/next/')
        self.assertEqual(response.status_code, 200)
