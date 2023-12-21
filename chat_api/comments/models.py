from django.db import models
from django.utils.translation import gettext as _
# Create your models here.

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    room_id = models.ForeignKey('rooms.Room', on_delete=models.CASCADE)
    content = models.JSONField(_("Content"), default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
            return self.content