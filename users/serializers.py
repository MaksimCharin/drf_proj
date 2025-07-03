from rest_framework import serializers
from users.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    paid_course_name = serializers.CharField(source='paid_course.name', read_only=True, allow_null=True)
    paid_lesson_name = serializers.CharField(source='paid_lesson.name', read_only=True, allow_null=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'user', 'user_email', 'payment_date',
            'paid_course', 'paid_course_name',
            'paid_lesson', 'paid_lesson_name',
            'amount', 'payment_method'
        )