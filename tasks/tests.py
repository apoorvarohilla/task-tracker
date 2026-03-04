from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from tasks.models import Task

class TaskAPITests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password1')
        self.admin = User.objects.create_superuser(username='admin', password='adminpassword')
        
        self.task1 = Task.objects.create(title='Task 1', description='Desc 1', owner=self.user1)
        self.task2 = Task.objects.create(title='Task 2', description='Desc 2', owner=self.user2)

        self.list_url = reverse('task-list')
        self.detail_url_user1 = reverse('task-detail', args=[self.task1.id])
        self.detail_url_user2 = reverse('task-detail', args=[self.task2.id])

    def test_unauthenticated_read_tasks(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_unauthenticated_create_task(self):
        data = {'title': 'New Task', 'description': 'Desc'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_create_task(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'New Task', 'description': 'Desc'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)
        self.assertEqual(Task.objects.last().owner, self.user1)

    def test_update_own_task(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'Updated Task 1'}
        response = self.client.patch(self.detail_url_user1, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Updated Task 1')

    def test_update_other_user_task_fails(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'Hacked Task 2'}
        response = self.client.patch(self.detail_url_user2, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_update_other_user_task(self):
        self.client.force_authenticate(user=self.admin)
        data = {'title': 'Admin Updated Task'}
        response = self.client.patch(self.detail_url_user1, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_filtering(self):
        Task.objects.create(title='Completed Task', completed=True, owner=self.user1)
        response = self.client.get(f"{self.list_url}?completed=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Completed Task')
