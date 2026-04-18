from rest_framework import serializers

from lms.models import Course, Lesson, Subscription
from lms.validators import LinkValidator


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [LinkValidator(field="link")]


class CourseSerializer(serializers.ModelSerializer):
    lesson_quantity = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lesson_quantity(self, instance):
        return instance.lessons.count()

    def get_is_subscribed(self, instance):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, course=instance
            ).exists()
        return False
