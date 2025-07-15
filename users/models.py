from django.contrib.auth.models import AbstractUser
from django.db import models
from materials.models import Course, Lesson
from users.managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True, verbose_name="почта", help_text="Укажите почту"
    )

    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="телефон",
        help_text="Укажите телефон",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="город",
        help_text="Укажите город",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="аватар"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='дата оплаты')
    paid_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='оплаченный курс')
    paid_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='оплаченный урок')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='сумма оплаты')
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES, verbose_name='способ оплаты')

    def __str__(self):
        if self.paid_course:
            return f"Оплата курса '{self.paid_course.name}' пользователем {self.user.email}"
        elif self.paid_lesson:
            return f"Оплата урока '{self.paid_lesson.name}' пользователем {self.user.email}"
        return f"Оплата пользователем {self.user.email}"

    class Meta:
        verbose_name = 'платеж'
        verbose_name_plural = 'платежи'


class StripeProductPrice(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='stripe_details', verbose_name='курс')
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='stripe_details', verbose_name='урок')
    stripe_product_id = models.CharField(max_length=255, verbose_name="ID продукта Stripe")
    stripe_price_id = models.CharField(max_length=255, verbose_name="ID цены Stripe")

    class Meta:
        verbose_name = 'Stripe Продукт/Цена'
        verbose_name_plural = 'Stripe Продукты/Цены'

    def __str__(self):
        if self.course:
            return f"Stripe для курса: {self.course.name}"
        elif self.lesson:
            return f"Stripe для урока: {self.lesson.name}"
        return "Stripe Product/Price (без привязки)"