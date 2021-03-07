from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


from django.urls import reverse

from .models import User


class UserTestCase(APITestCase):

    def tearDown(self):
        for user in User.objects.all():
            user.delete()

    def test_new_user_can_register(self):
        post_body = {
            'name': 'some dude',
            'email': 'somedude@somesite.com',
            'password': 'password123'
        }
        url = reverse('register')
        response = self.client.post(url, data=post_body)

        self.assertTrue(response.data.get('token'))
        self.assertTrue(response.data.get('user_id'))
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 201)


    def test_already_existing_user_can_login(self):
        user = User(name='some dude', email='somedude@somesite.com')
        user.set_password('password123')
        user.save()

        post_body = {
            'name': 'some dude',
            'email': 'somedude@somesite.com',
            'password': 'password123'
        }
        url = reverse('login')
        response = self.client.post(url, data=post_body)

        self.assertTrue(response.data.get('token'))
        self.assertTrue(response.data.get('user_id'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_log_out(self):
        user = User(name='some dude', email='somedude@somesite.com')
        user.set_password('password123')
        user.save()

        post_body = {
            'name': 'some dude',
            'email': 'somedude@somesite.com',
            'password': 'password123'
        }
        url = reverse('login')
        response = self.client.post(url, data=post_body)

        token = response.data.get('token')
        user.refresh_from_db()
        self.assertEqual(user.auth_token.key, token)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('logout')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 204)
        user.refresh_from_db()
        self.assertFalse(hasattr(user, 'auth_token'))

    def test_user_can_change_data(self):
        user = User(name='some dude', email='somedude@somesite.com')
        user.set_password('password123')
        user.save()

        token = Token.objects.create(user=user)

        put_body = {
            'name': 'some other dude',
            'email': 'someotherdude@somesite.com',
            'password': 'password1234'
        }
        url = reverse('users-api')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)
        response = self.client.put(url, data=put_body)

        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.name, 'some other dude')
        self.assertEqual(user.email, 'someotherdude@somesite.com')
        self.assertTrue(user.check_password('password1234'))
        self.assertTrue(response.data.get('password_changed'))

    def test_delete_user(self):
        user = User(name='some dude', email='somedude@somesite.com')
        user.set_password('password123')
        user.save()

        token = Token.objects.create(user=user)
        url = reverse('users-api')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(email='somedude@somesite.com'))

    def test_user_cant_register_more_than_once(self):
        post_body = {
            'name': 'some dude',
            'email': 'somedude@somesite.com',
            'password': 'password123'
        }
        url = reverse('register')
        first_response = self.client.post(url, data=post_body)
        self.assertEqual(first_response.status_code, 201)

        second_response = self.client.post(url, data=post_body)
        self.assertEqual(second_response.status_code, 400)

    def test_invalid_credentials_are_denied(self):
        user = User(name='some dude', email='somedude@somesite.com')
        user.set_password('password123')
        user.save()

        post_body = {
            'name': 'some dude',
            'email': 'somedude@somesite.com',
            'password': 'wrong'
        }
        url = reverse('login')
        response = self.client.post(url, data=post_body)

        self.assertEqual(response.status_code, 403)

    def test_user_api_doesnt_accept_requests_without_a_token(self):
        user = User(name='some dude', email='somedude@somesite.com')
        user.set_password('password123')
        user.save()

        put_body = {
            'name': 'some other dude',
            'email': 'someotherdude@somesite.com',
            'password': 'password1234'
        }
        url = reverse('users-api')
        response = self.client.put(url, data=put_body)

        self.assertEqual(response.status_code, 401)
