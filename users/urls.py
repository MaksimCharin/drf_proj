from django.urls import path
from users.views import PaymentListView
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment_list'),
]