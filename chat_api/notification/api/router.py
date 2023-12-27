from django.urls import path
from notification.api.views import NotificationListAPIView, NotificationDeleteApiView
urlpatterns = [
    # Crear y registrar en una sala
    path('notification/<int:pk>/', NotificationDeleteApiView.as_view(), name='room'),
    path('notifications/', NotificationListAPIView.as_view(), name='room'),
    
]