from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, \
    get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, Subscription
from lms.paginators import LessonPaginator, CoursePaginator
from lms.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner
from lms.tasks import send_course_update_notifications


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = CoursePaginator

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        """
            Полное обновление курса
        """
        response = super().update(request, *args, **kwargs)

        # Если обновление прошло успешно - запускаем рассылку
        if response.status_code == status.HTTP_200_OK:
            send_course_update_notifications.delay()

        return response

    def partial_update(self, request, *args, **kwargs):
        """
            Частичное обновление курса
        """
        response = super().partial_update(request, *args, **kwargs)

        # Если обновление прошло успешно - запускаем рассылку
        if response.status_code == status.HTTP_200_OK:
            send_course_update_notifications.delay()

        return response

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (~IsModerator, IsAuthenticated)
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = (IsModerator | IsOwner, IsAuthenticated)
        elif self.action == "destroy":
            self.permission_classes = (IsOwner, ~IsModerator, IsAuthenticated)
        return super().get_permissions()



class LessonCreateAPIView(CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = (~IsModerator, IsAuthenticated)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = (IsOwner | IsModerator, IsAuthenticated)
    pagination_class = LessonPaginator


class LessonRetrieveAPIView(RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = (IsOwner | IsModerator, IsAuthenticated)


class LessonUpdateAPIView(UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = (IsOwner | IsModerator, IsAuthenticated)


class LessonDestroyAPIView(DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = (IsOwner, IsAuthenticated)


class SubscriptionAPIView(APIView):
    """
        Управление подписками на курс
    """
    def post(self, request, *args, **kwargs):
        # Получаем пользователя
        user = request.user

        # Получаем course_id
        course_id = request.data.get('course_id')

        # Получаем объект курса или возвращаем 404
        course_item = get_object_or_404(Course, id=course_id)

        # Получаем объекты подписок по текущему пользователю и курсу
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
            status_code = status.HTTP_200_OK
        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена'
            status_code = status.HTTP_201_CREATED

        # Возвращаем ответ в API
        return Response(
            {"message": message, "course_id": course_id},
            status=status_code
        )