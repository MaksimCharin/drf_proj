from django.urls import path
from users.views import PaymentListView, UserCreateAPIView, UserListAPIView, \
    UserRetrieveAPIView, UserUpdateAPIView, UserDestroyAPIView
from users.apps import UsersConfig
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

app_name = UsersConfig.name

urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment_list'),

    # CRUD для пользователей
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('login', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', UserListAPIView.as_view(), name='user_list'),
    path('<int:pk>/', UserRetrieveAPIView.as_view(), name='user_retrieve'),
    path('<int:pk>/update/', UserUpdateAPIView.as_view(), name='user_update'),
    path('<int:pk>/delete/', UserDestroyAPIView.as_view(), name='user_delete'),
]