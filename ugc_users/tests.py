from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.utils import timezone
from .models import User
from .forms import UserRegistrationForm, UserProfileForm, ProfileUpdateForm
import os

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_verified)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(**self.user_data)
        self.assertEqual(admin_user.email, self.user_data['email'])
        self.assertEqual(admin_user.username, self.user_data['username'])
        self.assertTrue(admin_user.check_password(self.user_data['password']))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_verified)

    def test_user_str(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])

class UserFormsTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_registration_form_valid(self):
        form = UserRegistrationForm(data=self.user_data)
        self.assertTrue(form.is_valid())

    def test_user_registration_form_invalid(self):
        form = UserRegistrationForm(data={
            'email': 'invalid-email',
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertFalse(form.is_valid())

    def test_user_registration_form_unique_email(self):
        User.objects.create_user(
            email=self.user_data['email'],
            username='existinguser',
            password='testpass123'
        )
        form = UserRegistrationForm(data=self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_profile_update_form(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Test bio'
        }
        form = ProfileUpdateForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())

class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.login(email=self.user_data['email'], password=self.user_data['password'])

    def test_register_view(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

        response = self.client.post(reverse('users:register'), {
            'email': 'new@example.com',
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_login_view(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

        response = self.client.post(reverse('users:login'), {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, 302)

    def test_profile_view(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_settings_view(self):
        response = self.client.get(reverse('users:settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/settings.html')

        response = self.client.post(reverse('users:settings'), {
            'first_name': 'Updated',
            'last_name': 'Name'
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')

    def test_verify_email(self):
        self.user.is_verified = False
        self.user.save()
        token = self.user.generate_verification_token()
        response = self.client.get(reverse('users:verify_email', args=[token]))
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_resend_verification_email(self):
        self.user.is_verified = False
        self.user.save()
        response = self.client.post(reverse('users:resend_verification'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

class UserURLsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.login(email='test@example.com', password='testpass123')

    def test_urls(self):
        urls = [
            ('users:register', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:profile', None),
            ('users:settings', None),
            ('users:password_reset', None),
            ('users:password_reset_done', None),
            ('users:password_reset_confirm', {'uidb64': 'test', 'token': 'test'}),
            ('users:password_reset_complete', None),
            ('users:verify_email', {'token': 'test'}),
            ('users:resend_verification', None),
        ]

        for url_name, kwargs in urls:
            response = self.client.get(reverse(url_name, kwargs=kwargs))
            self.assertNotEqual(response.status_code, 404, f"URL {url_name} not found")
