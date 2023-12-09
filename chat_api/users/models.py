from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ADMIN = 'Admin'
    USER = 'User'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
    ]
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES, 
        default=USER
    )
    
    avatar = models.IntegerField(default=1)

    #TODO permisos
    #? Admin
    # tiene todos los permisos
    #? User
    # puede consultar room, crear room y eliminar o actualizar sus room creados
    # puede consultar comments, crear comments y eliminar o actualizar sus comments creados
    # Cambios para evitar conflictos en los accesos inversos


    # cambiar login a email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name']

    
    def full_name(self):
            return f"{self.firs_name} {self.last_name}"
        
    def __str__(self):
            return self.email