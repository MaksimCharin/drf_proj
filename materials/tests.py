from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from materials.models import Course, Lesson, Subscription


class LessonCRUDTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com', password='testpassword'
        )
        self.moderator = get_user_model().objects.create_user(
            email='moderator@example.com', password='modpassword', is_staff=True
        )

        self.moderator_group, created = Group.objects.get_or_create(name='Модераторы')
        self.moderator.groups.add(self.moderator_group)

        self.course = Course.objects.create(
            name='Test Course', owner=self.user
        )
        self.lesson = Lesson.objects.create(
            name='Test Lesson', course=self.course, owner=self.user
        )

    def test_lesson_create_as_owner(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'New Lesson',
            'course': self.course.id,
            'video_link': 'https://www.youtube.com/watch?v=test'
        }
        response = self.client.post(reverse('materials:lessons_create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.get(name='New Lesson').owner, self.user)

    def test_lesson_create_as_moderator_forbidden(self):
        self.client.force_authenticate(user=self.moderator)
        data = {
            'name': 'New Lesson by Moderator',
            'course': self.course.id,
            'video_link': 'https://www.youtube.com/watch?v=test'
        }
        response = self.client.post(reverse('materials:lessons_create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_create_with_invalid_link(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Lesson with Bad Link',
            'course': self.course.id,
            'video_link': 'https://badsite.com/video'
        }
        response = self.client.post(reverse('materials:lessons_create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_lesson_list_as_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('materials:lessons_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_lesson_list_as_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(reverse('materials:lessons_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_lesson_retrieve_as_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('materials:lessons_retrieve', args=[self.lesson.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Lesson')

    def test_lesson_retrieve_as_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(reverse('materials:lessons_retrieve', args=[self.lesson.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Lesson')

    def test_lesson_update_as_owner(self):
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Updated Lesson Name'}
        response = self.client.patch(reverse('materials:lessons_update', args=[self.lesson.pk]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, 'Updated Lesson Name')

    def test_lesson_update_as_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        data = {'name': 'Updated Lesson Name by Moderator'}
        response = self.client.patch(reverse('materials:lessons_update', args=[self.lesson.pk]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, 'Updated Lesson Name by Moderator')

    def test_lesson_delete_as_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('materials:lessons_delete', args=[self.lesson.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_as_moderator_forbidden(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(reverse('materials:lessons_delete', args=[self.lesson.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com', password='testpassword'
        )
        self.course = Course.objects.create(
            name='Subscription Test Course', owner=self.user
        )

    def test_subscribe_to_course(self):
        self.client.force_authenticate(user=self.user)
        data = {'course_id': self.course.id}
        response = self.client.post(reverse('materials:subscription'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена.')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        data = {'course_id': self.course.id}
        response = self.client.post(reverse('materials:subscription'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена.')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_course_list_shows_subscription_status(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('materials:course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['is_subscribed'], True)

        Subscription.objects.all().delete()
        response = self.client.get(reverse('materials:course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['is_subscribed'], False)