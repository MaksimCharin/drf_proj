from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from materials.models import Course, Lesson
from users.models import User


class Command(BaseCommand):
    help = 'Создает группу "Модераторы" и назначает ей необходимые права на просмотр и изменение курсов/уроков.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Начинаем инициализацию ролей ---'))

        moderators_group, created = Group.objects.get_or_create(name='Модераторы')
        if created:
            self.stdout.write(self.style.SUCCESS("Группа 'Модераторы' успешно создана."))
        else:
            self.stdout.write(self.style.WARNING("Группа 'Модераторы' уже существует."))

        try:
            course_content_type = ContentType.objects.get_for_model(Course)
            lesson_content_type = ContentType.objects.get_for_model(Lesson)
        except ContentType.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "Ошибка: Модели Course или Lesson не найдены. Убедитесь, что они существуют и вы запустили makemigrations/migrate."))
            return

        required_perms_codenames = [
            'view_course', 'change_course',
            'view_lesson', 'change_lesson',
        ]

        perms_to_add = []
        for perm_codename in required_perms_codenames:
            try:
                if 'course' in perm_codename:
                    content_type = course_content_type
                elif 'lesson' in perm_codename:
                    content_type = lesson_content_type
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Неизвестный codename разрешения: {perm_codename}. Пропускаем."))
                    continue

                perm = Permission.objects.get(content_type=content_type, codename=perm_codename)
                perms_to_add.append(perm)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f"Ошибка: Разрешение '{perm_codename}' не найдено. Убедитесь, что вы запустили 'python manage.py migrate'."))
                return

        moderators_group.permissions.clear()
        moderators_group.permissions.add(*perms_to_add)
        self.stdout.write(
            self.style.SUCCESS("Права на просмотр и изменение курсов/уроков успешно добавлены в группу 'Модераторы'."))

        try:
            moderator_user_email = 'admin@admin.com'
            moderator_user = User.objects.get(email=moderator_user_email)

            if not moderator_user.groups.filter(name='Модераторы').exists():
                moderator_user.groups.add(moderators_group)
                moderator_user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Пользователь {moderator_user.email} успешно добавлен в группу 'Модераторы'."))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Пользователь {moderator_user.email} уже находится в группе 'Модераторы'."))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f"Ошибка: Пользователь '{moderator_user_email}' не найден. Создайте его командой 'createsuperuser' или измените email в этом файле."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Произошла ошибка при добавлении пользователя в группу: {e}"))

        self.stdout.write(self.style.SUCCESS('--- Инициализация ролей завершена ---'))