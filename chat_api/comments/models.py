from django.db import models
from django.utils.translation import gettext as _
from users.models import User
from rooms.models import Room
# Create your models here.
from ckeditor.fields import RichTextField
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
            return self.content