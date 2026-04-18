from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, permissions
from rest_framework.filters import OrderingFilter
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from lms.models import Course, Lesson
from users.models import User, Payments
from users.permissions import IsOwnerOrAdmin
from users.serializers import (
    UserSerializer,
    PaymentsSerializer,
    UserUpdateSerializer,
    PublicUserSerializer,
    PaymentCreateSerializer,
    PaymentResponseSerializer,
    PaymentStatusSerializer,
)
from users.services import stripe_service


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
        context["request"] = self.request
        return context


class UserProfileView(RetrieveAPIView):
    """
    Просмотр своего профиля
    """

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
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
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("payment_date",)


class PaymentCreateAPIView(CreateAPIView):
    serializer_class = PaymentsSerializer
    queryset = Payments.objects.all()


class CreatePaymentView(APIView):
    """
    Создание платежа
    """

    def post(self, request):
        # Валидация входных данных
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id = serializer.validated_data["item_id"]
        item_type = serializer.validated_data["item_type"]

        # Получаем товар
        if item_type == "course":
            item = get_object_or_404(Course, id=item_id)
        else:
            item = get_object_or_404(Lesson, id=item_id)

        # Создаем запись о платеже
        payment = Payments.objects.create(
            user=request.user,
            paid_course=item if item_type == "course" else None,
            paid_lesson=item if item_type == "lesson" else None,
            payment_amount=item.price,
            payment_method="stripe",
            status="pending",
        )

        # Формируем URL для редиректа
        site_url = settings.SITE_URL
        success_url = f"{site_url}/users/payment-success/?session_id={{CHECKOUT_SESSION_ID}}&payment_id={payment.id}"
        cancel_url = f"{site_url}/users/payment-cancel/"

        # Создаем полный процесс оплаты в Stripe
        payment_data = stripe_service.create_full_payment_flow(
            product_name=item.name,
            amount=float(item.price),
            product_description=item.description,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "payment_id": payment.id,
                "user_id": request.user.id,
                "item_type": item_type,
                "item_id": item.id,
            },
        )

        # Обновляем платеж данными из Stripe
        payment.stripe_product_id = payment_data["product"]["id"]
        payment.stripe_price_id = payment_data["price"]["id"]
        payment.stripe_session_id = payment_data["session"]["id"]
        payment.stripe_checkout_url = payment_data["checkout_url"]
        payment.save()

        # Возвращаем ответ
        response_serializer = PaymentResponseSerializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PaymentStatusView(APIView):
    """
    Проверка статуса платежа
    """

    def get(self, request, payment_id):
        payment = get_object_or_404(Payments, id=payment_id, user=request.user)

        # Если есть session_id, проверяем в Stripe
        if payment.stripe_session_id and payment.status != "succeeded":
            try:
                session = stripe_service.retrieve_checkout_session(
                    payment.stripe_session_id
                )
                if session.get("payment_status") == "paid":
                    payment.status = "succeeded"
                    payment.save()
            except Exception:
                pass

        serializer = PaymentStatusSerializer(payment)
        return Response(serializer.data)


class PaymentSuccessView(APIView):
    """
    Обработка успешной оплаты (редирект от Stripe)
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        session_id = request.query_params.get("session_id")
        payment_id = request.query_params.get("payment_id")

        try:
            session = stripe_service.retrieve_checkout_session(session_id)
            payment = get_object_or_404(Payments, id=payment_id)

            if session.get("payment_status") == "paid":
                payment.status = "succeeded"
                payment.save()
                return Response({"success": True, "message": "Платеж успешно завершен"})

            return Response(
                {"success": False, "message": "Платеж не был завершен"}, status=400
            )

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class PaymentCancelView(APIView):
    """
    Обработка отмены оплаты
    """

    def get(self, request):
        return Response({"success": False, "message": "Оплата была отменена"})
