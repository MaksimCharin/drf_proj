from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from materials.models import Course, Lesson


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'name', 'preview', 'description', 'lessons_count', 'lessons')

    def get_lessons_count(self, obj):
        return obj.lessons.count()

