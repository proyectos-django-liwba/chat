from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.api.views import RegisterView, UserView, UserChangePasswordView

urlpatterns = [
  #auth
  path('auth/login/', TokenObtainPairView.as_view(), name='login'),
  path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
  #users
  path('auth/register/', RegisterView.as_view(), name='register'),
  path('auth/me/', UserView.as_view(), name='me'),
  path('auth/update-password/', UserChangePasswordView.as_view(), name='update-password'),
] 

""" from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.api.views import RegisterView, UserView

urlpatterns = [
    path('auth/register', RegisterView.as_view()),
    path('auth/login', TokenObtainPairView.as_view()),
    path('auth/token/refresh', TokenRefreshView.as_view()),
    path('auth/obtener', UserView.as_view()),
] """
