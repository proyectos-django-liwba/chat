from django.db import models
from django.db.models import SET_NULL
from users.models import User


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=300)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    users = models.ManyToManyField(User, related_name='rooms', blank=True)

    def __str__(self):
        return self.name
    
    def get_users_count(self):
        return self.users.count()
    
    def get_active_users_count(self):
        return self.users.filter(is_active=True).count()
