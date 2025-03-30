from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Content, ContentCategory, ContentTag
from .forms import ContentForm
from datetime import datetime, timedelta

User = get_user_model()

class ContentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.category = ContentCategory.objects.create(
            name='Test Category',
            description='Test category description'
        )
        self.tag = ContentTag.objects.create(name='Test Tag')

    def test_create_content(self):
        content = Content.objects.create(
            title='Test Content',
            description='Test description',
            platform='instagram',
            status='draft',
            author=self.user,
            category=self.category
        )
        content.tags.add(self.tag)

        self.assertEqual(content.title, 'Test Content')
        self.assertEqual(content.description, 'Test description')
        self.assertEqual(content.platform, 'instagram')
        self.assertEqual(content.status, 'draft')
        self.assertEqual(content.author, self.user)
        self.assertEqual(content.category, self.category)
        self.assertIn(self.tag, content.tags.all())

    def test_content_str(self):
        content = Content.objects.create(
            title='Test Content',
            description='Test description',
            platform='instagram',
            status='draft',
            author=self.user,
            category=self.category
        )
        self.assertEqual(str(content), 'Test Content')

    def test_content_scheduling(self):
        future_date = datetime.now() + timedelta(days=1)
        content = Content.objects.create(
            title='Scheduled Content',
            description='Test description',
            platform='instagram',
            status='scheduled',
            author=self.user,
            category=self.category,
            scheduled_date=future_date
        )
        self.assertEqual(content.status, 'scheduled')
        self.assertEqual(content.scheduled_date, future_date)

class ContentFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.category = ContentCategory.objects.create(
            name='Test Category',
            description='Test category description'
        )
        self.tag = ContentTag.objects.create(name='Test Tag')

    def test_content_form_valid(self):
        form_data = {
            'title': 'Test Content',
            'description': 'Test description',
            'platform': 'instagram',
            'status': 'draft',
            'category': self.category.id,
            'tags': [self.tag.id]
        }
        form = ContentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_content_form_invalid(self):
        form_data = {
            'title': '',
            'description': 'Test description',
            'platform': 'invalid_platform',
            'status': 'invalid_status'
        }
        form = ContentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('platform', form.errors)
        self.assertIn('status', form.errors)

class ContentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.login(email='test@example.com', password='testpass123')
        self.category = ContentCategory.objects.create(
            name='Test Category',
            description='Test category description'
        )
        self.content = Content.objects.create(
            title='Test Content',
            description='Test description',
            platform='instagram',
            status='draft',
            author=self.user,
            category=self.category
        )

    def test_content_list_view(self):
        response = self.client.get(reverse('content:content_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/content_list.html')

    def test_content_detail_view(self):
        response = self.client.get(reverse('content:content_detail', args=[self.content.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/content_detail.html')

    def test_content_create_view(self):
        response = self.client.get(reverse('content:content_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/content_form.html')

        response = self.client.post(reverse('content:content_create'), {
            'title': 'New Content',
            'description': 'New description',
            'platform': 'instagram',
            'status': 'draft',
            'category': self.category.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Content.objects.filter(title='New Content').exists())

    def test_content_update_view(self):
        response = self.client.get(reverse('content:content_update', args=[self.content.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'content/content_form.html')

        response = self.client.post(reverse('content:content_update', args=[self.content.id]), {
            'title': 'Updated Content',
            'description': 'Updated description',
            'platform': 'instagram',
            'status': 'draft',
            'category': self.category.id
        })
        self.assertEqual(response.status_code, 302)
        self.content.refresh_from_db()
        self.assertEqual(self.content.title, 'Updated Content')
        self.assertEqual(self.content.description, 'Updated description')

    def test_content_delete_view(self):
        response = self.client.post(reverse('content:content_delete', args=[self.content.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Content.objects.filter(id=self.content.id).exists())

class ContentURLsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.login(email='test@example.com', password='testpass123')
        self.content = Content.objects.create(
            title='Test Content',
            description='Test description',
            platform='instagram',
            status='draft',
            author=self.user,
            category=ContentCategory.objects.create(name='Test Category')
        )

    def test_urls(self):
        urls = [
            ('content:content_list', None),
            ('content:content_detail', {'pk': self.content.id}),
            ('content:content_create', None),
            ('content:content_update', {'pk': self.content.id}),
            ('content:content_delete', {'pk': self.content.id}),
        ]

        for url_name, kwargs in urls:
            response = self.client.get(reverse(url_name, kwargs=kwargs))
            self.assertNotEqual(response.status_code, 404, f"URL {url_name} not found")
