from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from materials.models import Course, Lesson, Subscription
from materials.serializers import CourseSerializer, LessonDetailSerializer
from materials.permissions import IsModerator, IsOwner
from materials.paginators import MaterialPaginator
from materials.tasks import send_course_update_notification


# ViewSet (курс)
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all().order_by('pk')
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = MaterialPaginator

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        send_course_update_notification.delay(serializer.instance.id)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.none()

        if user.groups.filter(name='Модераторы').exists():
            return Course.objects.all().order_by('pk')
        return Course.objects.filter(owner=user).order_by('pk')


# Generics (уроки)
class LessonCreateAPIView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    permission_classes = (IsAuthenticated, ~IsModerator)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(ListAPIView):
    queryset = Lesson.objects.all().order_by('pk')
    serializer_class = LessonDetailSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = MaterialPaginator

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all().order_by('pk')
        return Lesson.objects.filter(owner=user).order_by('pk')


class LessonRetrieveAPIView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    permission_classes = (IsAuthenticated, IsModerator | IsOwner)


class LessonUpdateAPIView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    permission_classes = (IsAuthenticated, IsModerator | IsOwner)


class LessonDestroyAPIView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    permission_classes = (IsAuthenticated, IsOwner)


class SubscriptionAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get('course_id')

        if not course_id:
            return Response({"errors": {"course_id": "Не указан ID курса."}}, status=status.HTTP_400_BAD_REQUEST)

        course_item = get_object_or_404(Course, pk=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена.'
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена.'

        return Response({"message": message})


class PaymentSuccessView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Оплата успешно завершена!"})

class PaymentCancelView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Оплата отменена."})
