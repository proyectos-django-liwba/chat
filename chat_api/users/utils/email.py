from django.core.mail import send_mail
from django.conf import settings
from users.models import User
import jwt
import logging
import secrets

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def enviar_correo_verificacion(serializer):
    try:
        payload = {
            'user': serializer.validated_data.get('first_name', 'Usuario Desconocido'),
            'exp': datetime.utcnow() + timedelta(days=1)
        }

        # Generar el token JWT
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        activation_link = f'http://localhost:5173/login/{token}/'

        send_mail(
            'Verificar cuenta',
            f'Activa tu cuenta en el siguiente enlace: {activation_link}',
            settings.EMAIL_HOST_USER,
            [serializer.validated_data.get('email')],
            fail_silently=False,
        )

        # Devuelve True si el correo se envía correctamente
        return True
    except Exception as e:
        # Loguea el error
        logger.error(f"Error al enviar el correo electrónico: {e}")
        # Devuelve False si hay un error al enviar el correo
        return False
