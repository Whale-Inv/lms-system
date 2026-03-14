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
