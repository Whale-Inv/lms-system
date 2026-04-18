from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription


class LessonTestCase(APITestCase):
    """
    Тесты для проверки корректности работы CRUD уроков
    """

    def setUp(self):
        user = get_user_model()

        self.user = user.objects.create(email="test@test.com")
        self.user.set_password("testpass123")
        self.user.save()

        self.course = Course.objects.create(
            name="Тестовый курс",
            description="Описание тестового курса",
            owner=self.user,
        )

        self.lesson = Lesson.objects.create(
            name="test",
            description="test",
            link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            course=self.course,
            owner=self.user,
        )

        self.lesson_data = {
            "name": "Тестовый урок",
            "description": "Описание тестового урока",
            "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "course": self.course.id,
        }

        self.client.force_authenticate(user=self.user)

    def test_create_lesson(self):
        """Тестирование создания урока"""

        response = self.client.post("/lesson/create/", self.lesson_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        # Проверяем только нужные поля
        self.assertEqual(data["name"], "Тестовый урок")
        self.assertEqual(data["description"], "Описание тестового урока")
        self.assertEqual(data["preview"], None)
        self.assertEqual(data["link"], "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(data["course"], 1)
        self.assertEqual(data["owner"], 1)

        # Проверяем, что есть дополнительные поля (но не проверяем их значение)
        self.assertIn("price", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

        self.assertTrue(Lesson.objects.all().exists())

    def test_create_lesson_by_moderator(self):
        """Тестирование создания урока модератором"""

        user = get_user_model()
        other_user = user.objects.create(email="other@test.com")
        other_user.set_password("123")
        from django.contrib.auth.models import Group

        moderator_group, _ = Group.objects.get_or_create(name="Модераторы")
        other_user.groups.add(moderator_group)

        self.client.force_authenticate(user=other_user)

        response = self.client.post("/lesson/create/", self.lesson_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lessons(self):
        """Тестирование редактирования урока"""

        update_data = {
            "name": "Обновленное название",
            "description": "Обновленное описание",
            "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }

        response = self.client.patch(
            f"/lesson/update/{self.lesson.id}/", data=update_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_lessons(self):
        """Тестирование вывода списка уроков"""

        response = self.client.get("/lessons/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertIsNone(data["next"])
        self.assertIsNone(data["previous"])

        lesson_data = data["results"][0]
        self.assertEqual(lesson_data["name"], "test")
        self.assertEqual(lesson_data["description"], "test")
        self.assertEqual(
            lesson_data["link"], "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        self.assertEqual(lesson_data["course"], self.course.id)
        self.assertEqual(lesson_data["owner"], self.user.id)
        self.assertIsNone(lesson_data["preview"])

    def test_retrieve_lesson(self):
        """Тестирование просмотра одного урока"""
        response = self.client.get(f"/lesson/{self.lesson.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["name"], self.lesson.name)
        self.assertEqual(data["description"], self.lesson.description)
        self.assertEqual(data["link"], self.lesson.link)
        self.assertEqual(data["course"], self.course.id)
        self.assertEqual(data["owner"], self.user.id)

        self.assertEqual(data["id"], self.lesson.id)

    def test_delete_lesson(self):
        """Тестирование удаления урока"""
        response = self.client.delete(
            f"/lesson/delete/{self.lesson.id}/",
        )

        self.assertEqual(self.lesson.owner, self.user)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_as_other_user(self):
        """
        Тестирование удаления урока другим пользователем
        """
        user = get_user_model()
        other_user = user.objects.create(email="other@test.com")
        other_user.set_password("123")
        self.client.force_authenticate(user=other_user)

        response = self.client.delete(f"/lesson/delete/{self.lesson.id}/")

        self.assertEqual(response.status_code, 403)

    def test_delete_lesson_as_moderator(self):
        """
        Тестирование удаления урока модератором
        """
        user = get_user_model()
        other_user = user.objects.create(email="other@test.com")
        other_user.set_password("123")
        from django.contrib.auth.models import Group

        moderator_group, _ = Group.objects.get_or_create(name="Модераторы")
        self.user.groups.add(moderator_group)
        self.client.force_authenticate(user=other_user)

        response = self.client.delete(f"/lesson/delete/{self.lesson.id}/")

        self.assertEqual(response.status_code, 403)

    def test_subscribe_to_course(self):
        """Тестирование подписки на курс"""

        data = {"course_id": self.course.id}
        response = self.client.post("/subscriptions/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Подписка добавлена")

        # Проверяем, что подписка создалась в БД
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe_from_course(self):
        """Тестирование отписки от курса"""
        Subscription.objects.create(user=self.user, course=self.course)
        data = {"course_id": self.course.id}
        response = self.client.post("/subscriptions/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")

        # Проверяем, что подписка удалилась из БД
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )
