from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_get(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_post_success(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'Str0ngP@ss123!',
            'password2': 'Str0ngP@ss123!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_post_weak_password(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': '123',
            'password2': '123',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username(self):
        User.objects.create_user('existing', 'ex@test.com', 'pass123')
        data = {
            'username': 'existing',
            'email': 'new@test.com',
            'password1': 'Str0ngP@ss123!',
            'password2': 'Str0ngP@ss123!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)

    def test_register_auto_login(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'Str0ngP@ss123!',
            'password2': 'Str0ngP@ss123!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        # Check if user is logged in by accessing a protected page
        self.assertEqual(response.status_code, 302)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'Str0ngP@ss!')

    def test_login_get(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_success(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'Str0ngP@ss!',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_post_invalid(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'testuser', 'test@test.com', 'Str0ngP@ss!',
            first_name='Test', last_name='User'
        )
        self.client.login(username='testuser', password='Str0ngP@ss!')

    def test_profile_get(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_update(self):
        response = self.client.post(reverse('accounts:profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.email, 'updated@test.com')

    def test_profile_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)