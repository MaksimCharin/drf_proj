from rest_framework import serializers
from materials.models import Course, Lesson, Subscription
from materials.validators import LinkValidator

class LessonShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'name')

class LessonDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [LinkValidator(field='video_link')]

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonShortSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()


    class Meta:
        model = Course
        fields = ('id', 'name', 'preview', 'description', 'lessons_count', 'lessons')

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False