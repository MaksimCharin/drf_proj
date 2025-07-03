from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from materials.models import Course, Lesson
from users.models import Payment

import datetime
import random

class Command(BaseCommand):
    help = 'Создает примеры данных о платежах'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        user1, created = User.objects.get_or_create(email='testuser1@example.com', defaults={})
        if created:
            user1.set_password('password123')
            user1.is_staff = True
            user1.is_superuser = True
            user1.save()
            self.stdout.write(self.style.SUCCESS(f'Создан тестовый пользователь: {user1.email}'))

        user2, created = User.objects.get_or_create(email='testuser2@example.com', defaults={})
        if created:
            user2.set_password('password123')
            user2.save()
            self.stdout.write(self.style.SUCCESS(f'Создан тестовый пользователь: {user2.email}'))

        course1, created = Course.objects.get_or_create(name='Python для начинающих', defaults={'description': 'Курс по основам Python'})
        if created: self.stdout.write(self.style.SUCCESS(f'Создан курс: {course1.name}'))
        course2, created = Course.objects.get_or_create(name='Django Framework', defaults={'description': 'Продвинутый курс по Django'})
        if created: self.stdout.write(self.style.SUCCESS(f'Создан курс: {course2.name}'))

        lesson1, created = Lesson.objects.get_or_create(name='Введение в Django', course=course2, defaults={'description': 'Первый урок Django'})
        if created: self.stdout.write(self.style.SUCCESS(f'Создан урок: {lesson1.name}'))
        lesson2, created = Lesson.objects.get_or_create(name='Функции Python', course=course1, defaults={'description': 'Урок по функциям'})
        if created: self.stdout.write(self.style.SUCCESS(f'Создан урок: {lesson2.name}'))

        Payment.objects.all().delete()
        self.stdout.write(self.style.WARNING('Удалены существующие платежи.'))

        payments_data = [
            {
                'user': user1,
                'payment_date': datetime.datetime(2024, 1, 15, 10, 0, 0, tzinfo=datetime.timezone.utc),
                'paid_course': course1,
                'amount': 100.00,
                'payment_method': 'cash'
            },
            {
                'user': user2,
                'payment_date': datetime.datetime(2024, 1, 16, 11, 30, 0, tzinfo=datetime.timezone.utc),
                'paid_lesson': lesson1,
                'amount': 25.00,
                'payment_method': 'transfer'
            },
            {
                'user': user1,
                'payment_date': datetime.datetime(2024, 1, 17, 9, 0, 0, tzinfo=datetime.timezone.utc),
                'paid_course': course2,
                'amount': 150.00,
                'payment_method': 'cash'
            },
            {
                'user': user2,
                'payment_date': datetime.datetime(2024, 1, 18, 14, 15, 0, tzinfo=datetime.timezone.utc),
                'paid_lesson': lesson2,
                'amount': 30.00,
                'payment_method': 'transfer'
            }
        ]

        for data in payments_data:
            Payment.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f'Платеж для пользователя {data["user"].email} успешно создан'))
        self.stdout.write(self.style.SUCCESS('Все примеры платежей успешно созданы!'))
