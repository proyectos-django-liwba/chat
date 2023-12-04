from django.core.mail import send_mail
from django.conf import settings
from users.models import User
import jwt
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def enviar_correo_verificacion(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1)  # Configura la expiración del token
    }

    # Generar el token JWT
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    activation_link = f'https://tu-sitio.com/activar-cuenta/{token}/'

    try:
        send_mail(
            'Verificar cuenta',
            f'Activa tu cuenta en el siguiente enlace: {activation_link}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error al enviar el correo electrónico: {e}")

