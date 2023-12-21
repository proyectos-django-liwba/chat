from django.urls import path
from comments.api.views import CommentListAPIView,CommentDetailAPIView
urlpatterns = [
    # Crear y registrar en una sala
    path('comments/', CommentListAPIView.as_view(), name='comments'),
    path('comments/<int:comments_id>/', CommentDetailAPIView.as_view(), name='comments'),

]