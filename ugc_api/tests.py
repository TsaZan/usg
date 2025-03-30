from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from ugc_content.models import Content, Category, Tag

User = get_user_model()

class ContentAPITests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        # Create test tag
        self.tag = Tag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )

        # Create test content
        self.content = Content.objects.create(
            title='Test Content',
            description='Test Description',
            content_type='POST',
            user=self.user,
            category=self.category,
            platform='instagram'
        )
        self.content.tags.add(self.tag)

    def test_list_contents(self):
        url = reverse('content-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_content(self):
        url = reverse('content-list')
        data = {
            'title': 'New Content',
            'description': 'New Description',
            'content_type': 'POST',
            'category': self.category.id,
            'platform': 'instagram'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Content.objects.count(), 2)

    def test_retrieve_content(self):
        url = reverse('content-detail', args=[self.content.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.content.title)

    def test_update_content(self):
        url = reverse('content-detail', args=[self.content.id])
        data = {
            'title': 'Updated Content',
            'description': 'Updated Description'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.content.refresh_from_db()
        self.assertEqual(self.content.title, 'Updated Content')

    def test_delete_content(self):
        url = reverse('content-detail', args=[self.content.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Content.objects.count(), 0)

    def test_approve_content(self):
        url = reverse('content-approve', args=[self.content.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Non-staff user

        # Create staff user and test
        staff_user = User.objects.create_user(
            username='staffuser',
            password='testpass123',
            email='staff@example.com',
            is_staff=True
        )
        self.client.force_authenticate(user=staff_user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.content.refresh_from_db()
        self.assertEqual(self.content.status, Content.Status.APPROVED)

class CategoryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

    def test_list_categories(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_category(self):
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'slug': 'new-category'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

class TagAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.tag = Tag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )

    def test_list_tags(self):
        url = reverse('tag-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_tag(self):
        url = reverse('tag-list')
        data = {
            'name': 'New Tag',
            'slug': 'new-tag'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 2)
