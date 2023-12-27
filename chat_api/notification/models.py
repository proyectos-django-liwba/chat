from django.db import models
from django.db.models import SET_NULL
from users.models import User
from rooms.models import Room


class Notification(models.Model):
    CHOICES = (
        (1, 'Opción 1'),
        (2, 'Opción 2'),
    )
    description = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(Room, on_delete=SET_NULL, null=True)
    user= models.ForeignKey(User, on_delete=SET_NULL, null=True)
    users = models.ManyToManyField(User, related_name='notifications', blank=True)
    type = models.IntegerField(choices=CHOICES,default=0)
    
    
    