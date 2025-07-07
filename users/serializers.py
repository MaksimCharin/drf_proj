from rest_framework import serializers
from users.models import Payment, User


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'city', 'avatar', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)