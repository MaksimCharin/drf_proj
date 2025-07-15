from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.urls import reverse

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer
from materials.models import Course, Lesson
from materials.services import get_or_create_stripe_product_price, create_stripe_checkout_session


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = {
        'paid_course': ['exact'],
        'paid_lesson': ['exact'],
        'payment_method': ['exact'],
    }

    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']


# CRUD для пользователей
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class PaymentSuccessView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Оплата успешно завершена!"})

class PaymentCancelView(APIView):

    def get(self, request, *args, **kwargs):
        return Response({"message": "Оплата отменена."})


class CreateStripeCheckoutSessionAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')
        amount = request.data.get('amount')

        if not amount:
            return Response({"error": "Не указана сумма оплаты."}, status=status.HTTP_400_BAD_REQUEST)

        if not (course_id or lesson_id):
            return Response({"error": "Необходимо указать ID курса или урока."}, status=status.HTTP_400_BAD_REQUEST)

        item = None
        item_type = None
        if course_id:
            item = get_object_or_404(Course, pk=course_id)
            item_type = 'course'
        elif lesson_id:
            item = get_object_or_404(Lesson, pk=lesson_id)
            item_type = 'lesson'

        stripe_details = get_or_create_stripe_product_price(item, amount)

        if not stripe_details or not stripe_details.stripe_price_id:
            return Response({"error": "Не удалось создать продукт/цену в Stripe."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        success_url = request.build_absolute_uri(reverse('users:payment_success'))
        cancel_url = request.build_absolute_uri(reverse('users:payment_cancel'))

        checkout_session_url = create_stripe_checkout_session(
            price_id=stripe_details.stripe_price_id,
            user_email=request.user.email,
            success_url=success_url,
            cancel_url=cancel_url
        )

        if checkout_session_url:
            Payment.objects.create(
                user=request.user,
                paid_course=item if item_type == 'course' else None,
                paid_lesson=item if item_type == 'lesson' else None,
                amount=amount,
                payment_method='transfer'
            )
            return Response({"checkout_url": checkout_session_url})
        else:
            return Response({"error": "Не удалось создать сессию оплаты Stripe."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
