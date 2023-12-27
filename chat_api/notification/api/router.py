from django.urls import path
from notification.api.views import NotificationListAPIView
urlpatterns = [
    # Crear y registrar en una sala
    path('notification/<int:pk>/', NotificationListAPIView.as_view(), name='room'),

    
]