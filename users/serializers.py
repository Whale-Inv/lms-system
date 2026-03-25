from rest_framework import serializers

from users.models import User, Payments


class PaymentsSerializer(serializers.ModelSerializer):
    """ Основной сериализатор платежей"""
    class Meta:
        model = Payments
        fields = "__all__"


class PaymentCreateSerializer(serializers.Serializer):
    """ Сериализатор для создания платежа """
    item_id = serializers.IntegerField()
    item_type = serializers.ChoiceField(choices=['course', 'lesson'])


class PaymentResponseSerializer(serializers.ModelSerializer):
    """ Сериализатор для ответа о создании платежа """
    checkout_url = serializers.CharField(source='stripe_checkout_url')
    item_name = serializers.SerializerMethodField()

    class Meta:
        model = Payments
        fields = ['id', 'checkout_url', 'payment_amount', 'item_name', 'status']

    def get_item_name(self, obj):
        item = obj.paid_course or obj.paid_lesson
        return item.name if item else None


class PaymentStatusSerializer(serializers.ModelSerializer):
    """ Сериализатор для статуса платежа """
    item_name = serializers.SerializerMethodField()

    class Meta:
        model = Payments
        fields = ['id', 'status', 'payment_amount', 'item_name', 'payment_date']

    def get_item_name(self, obj):
        item = obj.paid_course or obj.paid_lesson
        return item.name if item else None


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentsSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("email", "phone", "city", "avatar", "payments")


class PublicUserSerializer(serializers.ModelSerializer):
    """
    Публичный сериализатор для чужих профилей. Только общая информация
    """
    class Meta:
        model = User
        fields = ("id", "email", "city", "avatar")


class UserUpdateSerializer(serializers.ModelSerializer):
    """
        Сериализатор для обновления профиля пользователя
    """
    class Meta:
        model = User
        fields = ("first_name", "last_name","phone", "city", "avatar")
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False},
            'city': {'required': False},
            'avatar': {'required': False}
        }
    @staticmethod
    def validate_avatar(value):
        # Валидация размера аватара
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Размер файла не должен превышать 5MB')
        return value