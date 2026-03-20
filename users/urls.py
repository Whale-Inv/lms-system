from django.urls import path
from rest_framework.permissions import AllowAny

from users.apps import UsersConfig
from users.views import PaymentsListAPIView, UserCreateAPIView, UserProfileView, UserDetailView, UserUpdateAPIView, \
    UserDeleteView, CreatePaymentView, PaymentStatusView, PaymentSuccessView, PaymentCancelView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = UsersConfig.name


urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/update/', UserUpdateAPIView.as_view(), name='user-update'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('login/', TokenObtainPairView.as_view(permission_classes = (AllowAny,)), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(permission_classes = (AllowAny,)), name='token_refresh'),

    path('payments/', PaymentsListAPIView.as_view(), name='payments-list'),
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('payment-status/<int:payment_id>/', PaymentStatusView.as_view(), name='payment-status'),
    path('payment-success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('payment-cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
]