from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User, Payments
from users.permissions import IsOwnerOrAdmin
from users.serializers import UserSerializer, PaymentsSerializer, UserUpdateSerializer, PublicUserSerializer


class UserCreateAPIView(CreateAPIView):
    """
        Создание пользователя
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserUpdateAPIView(UpdateAPIView):
    """
        Обновление профиля пользователя
    """
    queryset = User.objects.all()
    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class UserProfileView(RetrieveAPIView):
    """
        Просмотр своего профиля
    """
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer


class UserDetailView(RetrieveAPIView):
    """
        Просмотр профиля другого пользователя
    """
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer


class UserDeleteView(DestroyAPIView):
    """
        Удаление пользователя
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin, IsAuthenticated]

    def perform_destroy(self, instance):
        instance.delete()


class PaymentsListAPIView(generics.ListAPIView):
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('paid_course', 'paid_lesson', 'payment_method')
    ordering_fields = ("payment_date",)
