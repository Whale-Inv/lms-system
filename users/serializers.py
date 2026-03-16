from rest_framework import serializers

from users.models import User, Payments


class PaymentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payments
        fields = "__all__"


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