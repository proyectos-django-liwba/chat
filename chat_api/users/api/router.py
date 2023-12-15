from django.urls import path,include
from rest_framework_simplejwt.views import TokenRefreshView
from users.api.views import RegisterView, UserView, UserChangePasswordView, CustomTokenObtainPairView, VerificarCuentaView, ChangePasswordView

urlpatterns = [
  #auth
  path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
  path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
  path('auth/verify-otp/', VerificarCuentaView.as_view(), name='verify-otp'),
  #users
  path('auth/register/', RegisterView.as_view(), name='register'),
  path('auth/update-password/', ChangePasswordView.as_view(), name='update-password'),
  path('user/<int:pk>/', UserView.as_view(), name='user'),



] 
