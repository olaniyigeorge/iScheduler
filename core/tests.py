from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .views import Index

class IndexTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.url = reverse('index')

    def test_index_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("iScheduler", response.data['name'])
        self.assertIn("current_schedule", response.data)
        self.assertIn("tasks", response.data)
        self.assertIn("schedules", response.data)
        self.assertIn("with", response.data)
        self.assertIn("without", response.data)

    def test_index_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("iScheduler", response.data['name'])
        self.assertIn("current_schedule", response.data)
        self.assertIn("tasks", response.data)
        self.assertIn("schedules", response.data)
        self.assertIn("with", response.data)
        self.assertIn("without", response.data)