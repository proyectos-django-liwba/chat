from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import os
from users.api.serializers import (
  UserRegisterSerializer,
  UserSerializer, 
  UserUpdateSerializer,
  VerificarCuentaSerializer,
  UserUpdatePathSerializer,
  UserChangePasswordRecoverSerializer,
)

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import jwt
from django.conf import settings
from users.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from users.api.permissions import IsOwner
from rest_framework.exceptions import PermissionDenied
from django.conf import settings
from users.models import User
import logging
from datetime import datetime, timedelta
from rest_framework import serializers
from django.contrib.auth import get_user_model
import base64
import os
from email.mime.image import MIMEImage
from rest_framework.generics import UpdateAPIView

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    # Definir que petición se puede hacer a este endpoint
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            # Ejecutar el método post de la clase padre
            response = super().post(request, *args, **kwargs)

            if response.status_code == status.HTTP_200_OK:
                # Obtener el ID del usuario desde el token de acceso
                access_token = response.data.get('access')
                user_id = AccessToken(access_token).get('user_id')

                # Obtener el usuario utilizando el ID
                user = User.objects.get(id=user_id)

                # Verificar si el usuario está verificado
                if not user.is_verified:
                    return Response(
                        {"error": "El usuario no está verificado."},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                user.last_login = datetime.now()
                user.save()

                # Serializar y agregar los detalles del usuario a la respuesta del token
                user_serializer = UserSerializer(user)
                user_data = user_serializer.data

                # Crear un nuevo diccionario de respuesta con el orden deseado
                new_response_data = {
                    'user': user_data,
                    'access': response.data['access'],
                    'refresh': response.data['refresh']
                }

                # Devolver la respuesta con el nuevo orden
                return Response(new_response_data, status=response.status_code)

        except Exception as e:
            # Personalizar la respuesta en caso de un error
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Ocurrió un error al verificar las credenciales"})

        # Si no hay un error y la respuesta es exitosa, devolver la respuesta original
        return response


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            # Leer los datos del request
            serializer = UserRegisterSerializer(data=request.data)

            # Validar los datos
            if serializer.is_valid(raise_exception=True):
                # Obtener y eliminar la contraseña del diccionario de datos
                password = serializer.validated_data.get('password')
                del serializer.validated_data['password']

                # Crear la instancia del usuario sin la contraseña
                user = User(**serializer.validated_data)

                # Validar y establecer la contraseña
                if password:
                    user.set_password(password)

                # Guardar el usuario
                user.save()

                # Generar el token JWT
                payload = {
                    'user_id': user.id,
                    'exp': datetime.utcnow() + timedelta(days=365 * 100)
                }
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

                # Guardar el token en el campo 'otp' del usuario
                user.otp = token
                user.save()
                activation_link = settings.ACTIVATION_URL.format(token=token)
                image_path_logo = os.path.join(settings.BASE_DIR, 'static', 'admin', 'img', 'logo.png')

                # Leer imágenes y convertirlas a base64
                with open(image_path_logo, "rb") as image_file:
                    image_base64_logo = base64.b64encode(image_file.read()).decode('utf-8')

                # Construir el enlace de activación
                activation_link = settings.ACTIVATION_URL.format(token=token)

                # Enviar el correo electrónico
                subject = 'Verificar cuenta'
                text_content = f'Haz clic en el siguiente enlace para verificar tu cuenta: {activation_link}'
                html_content = render_to_string('Email.html', {'user': user, "activation_link": activation_link})

                from_email = 'practicaprograuniversidad@gmail.com'
                to_email = [user.email]

                msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                msg.attach_alternative(html_content, "text/html")

                # Adjuntar las imágenes
                msg_img_logo = MIMEImage(base64.b64decode(image_base64_logo), name='logo.png')

                msg_img_logo.add_header('Content-ID', '<logo_image>')
                msg.attach(msg_img_logo)


                msg.send()

                # Respuesta en caso de éxito
                return Response(status=status.HTTP_201_CREATED, data={"message": "Usuario creado correctamente"})


        except serializers.ValidationError as validation_error:
            # Manejar errores de validación
            error_messages = {"message": []}
            
            for field, errors in validation_error.detail.items():
                error_messages["message"].extend([str(error) for error in errors])
            
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": error_messages})


        except Exception as e:
            # Loguea el error
            user.delete()
            logger.error(f"Error al registrar usuario: {e}")

        # Respuesta en caso de error
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": "Ocurrió un error al crear el usuario"})
    
    
class UserView(APIView):
  # seguridad para el endpoint, solo usuarios autenticados
  permission_classes = [IsOwner]
  
  #definir que petición se puede hacer a este endpoint
  http_method_names = ['put', 'patch', 'delete']
  
    # actualizar usuario autenticado
  def patch(self, request, *args, **kwargs):
        try:
            user_id = kwargs.get('pk')
            # Obtener el usuario autenticado
            user = User.objects.get(id=request.user.id)

            # Verificar si el usuario autenticado tiene permisos para actualizar este usuario
            self.check_object_permissions(request, user)

            # Obtener el nuevo avatar del request
            new_avatar = request.data.get('avatar', None)

            # Validar que el nuevo avatar no sea nulo
            if new_avatar is not None:
                # Actualizar solo el campo 'avatar'
                user.avatar = new_avatar
                user.save()

                # Serializar y devolver la respuesta
                serializer = UserUpdatePathSerializer(user)
                return Response(
                    {"message": "Avatar actualizado correctamente", "user": serializer.data},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "El campo 'avatar' no puede ser nulo."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {"error": f"No se pudo actualizar el avatar: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

  def put(self, request, *args, **kwargs):
    try:
      # Obtener el ID del usuario que se va a actualizar desde los parámetros de la URL
      user_id = kwargs.get('pk')
      
      # Obtener el usuario autenticado
      user = User.objects.get(id=request.user.id)
      
      # Verificar si el usuario autenticado tiene permisos para actualizar este usuario
      self.check_object_permissions(request, user)
            
      # se agregan los nuevos datos y los datos anteriores
      serializer = UserUpdateSerializer(user, data=request.data)
      
      # validar los datos
      if serializer.is_valid(raise_exception=True):
        # guardar
        serializer.save()
        return Response(status=status.HTTP_200_OK, data={"message":"Usuario actualizado correctamente", "user":serializer.data})
    except PermissionDenied as e:
        # Manejar la excepción de permiso denegado
        return Response(status=status.HTTP_403_FORBIDDEN, data={"error": str(e)})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error":serializer.errors, "message":"No se pudo actualizar el usuario"})

  # elimina usuario autenticado
  def delete(self, request, *args, **kwargs):
    try:
        user_id = kwargs.get('pk')
        user = User.objects.get(id=user_id)   
        # Obtener el usuario autenticado
        user_auth = User.objects.get(id=request.user.id)
        
        # Verificar si el usuario autenticado tiene permisos para actualizar este usuario
        self.check_object_permissions(request, user_auth)

        # Cambiar el estado del usuario a inactivo en lugar de eliminarlo
        user.delete()

        return Response(
            {"message": "Usuario eliminado correctamente"},
            status=status.HTTP_200_OK
        )
    except PermissionDenied as e:
        # Manejar la excepción de permiso denegado
        return Response(status=status.HTTP_403_FORBIDDEN, data={"error": str(e)})  
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "Usuario no encontrado"})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "No se pudo desactivar el usuario"})
    
class ChangePasswordView(UpdateAPIView):
    serializer_class = UserChangePasswordRecoverSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        try:
            # Validar datos del serializer
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid(raise_exception=True):
                # Obtener el usuario autenticado
                user = self.get_object()

                # Verificar la contraseña actual
                old_password = serializer.validated_data.get('old_password')
                if not user.check_password(old_password):
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Contraseña actual incorrecta."})

                # Cambiar la contraseña
                new_password = serializer.validated_data.get('new_password')
                user.set_password(new_password)
                user.save()

                return Response(status=status.HTTP_200_OK, data={"message": "Contraseña actualizada correctamente."})
            else: 
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Faltan datos."})

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e), "message": "No se pudo actualizar la contraseña."})


class VerificarCuentaView(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = VerificarCuentaSerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                # Aquí asumimos que el token contiene información necesaria, como el ID del usuario o el correo electrónico
                token = serializer.data['otp']
                
                # Decodificar el token para obtener la información
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

                # Obtener el ID de usuario del payload
                user_id = payload.get('user_id')
                

                # Obtener el usuario y activarlo
                user = get_user_model().objects.get(pk=user_id)
                
                if user.is_verified:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "La cuenta ya está activada"})

                user.is_verified = True
                user.otp = None
                user.save()

            return Response(status=status.HTTP_200_OK, data={"message": "Cuenta activada correctamente!"})

        except jwt.ExpiredSignatureError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Token ha expirado"})

        except jwt.InvalidTokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Token no válido"})

        except get_user_model().DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "Usuario no encontrado"})

        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})     


class TokenGenerationError(Exception):
    pass

class EmailSendingError(Exception):
    pass


class RecuperarPasswordView(APIView):
    
    http_method_names = ['post', 'patch']
    
    
    @staticmethod
    def _generate_token(user):
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    
    def _send_reset_email(self, user, token, email):
        try:
            # Construir el enlace de activación
            recover_link = settings.RECOVER_PASSWORD_URL.format(token=token)

            # Lógica de envío de correo electrónico
            subject = 'Restablecimiento de contraseña de Chat Space'
            text_content = f'Haz clic en el siguiente enlace para cambiar tu contraseña: {recover_link}'
            html_content = render_to_string('RecuperarPassword.html', {'user': user, "recover_link": recover_link})

            from_email = 'practicaprograuniversidad@gmail.com'
            to_email = [email]  # Usar el correo electrónico proporcionado en lugar del correo del usuario

            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")

            # Adjuntar imágenes
            image_path_logo = os.path.join(settings.BASE_DIR, 'static', 'admin', 'img', 'logo.png')
            with open(image_path_logo, "rb") as image_file:
                image_base64_logo = base64.b64encode(image_file.read()).decode('utf-8')
            msg_img_logo = MIMEImage(base64.b64decode(image_base64_logo), name='logo.png')
            msg_img_logo.add_header('Content-ID', '<logo_image>')
            msg.attach(msg_img_logo)

            msg.send()
        except Exception as e:
            raise EmailSendingError(f"Error al enviar el correo: {str(e)}")
        
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            if not email:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Se requiere proporcionar un correo electrónico."})

            # Verificar si el usuario con el correo electrónico proporcionado existe
            user = User.objects.filter(email=email).first()
            if not user:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "No existe un usuario con este correo electrónico."})

            token = self._generate_token(user)

            # Guardar el token en el campo 'otp' del usuario
            user.otp = token
            user.save()

            # Enviar el correo de recuperación
            self._send_reset_email(user, token, email)

            return Response(status=status.HTTP_200_OK, data={"message": "Correo de recuperación enviado correctamente."})
        except EmailSendingError as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e), "message": "Error al enviar el correo de recuperación."})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e), "message": "No se pudo enviar el correo de recuperación."})   
    
    def patch(self, request, *args, **kwargs):
        data = request.data
        serializer = UserChangePasswordRecoverSerializer(data=data)

        try:
            
            if serializer.is_valid(raise_exception=True):
                
                token = serializer.validated_data['otp']

                # Decodificar el token para obtener la información
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

                # Obtener el ID de usuario del payload
                user_id = payload.get('user_id')

                user = get_user_model().objects.get(pk=user_id)

                if token == user.otp:
                    if serializer.validated_data['password'] == serializer.validated_data['confirm_password']:
                        # Utilizar set_password para almacenar la contraseña de forma segura
                        
                        user.set_password(serializer.validated_data['password'])
                        user.otp = None
                        user.save()
                        
                        return Response(status=status.HTTP_200_OK, data={"message": "Contraseña actualizada correctamente."})
                    else:
                        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Las contraseñas no coinciden."})
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Token no válido."})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Faltan datos."})

        except jwt.ExpiredSignatureError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "El token ha expirado."})

        except jwt.InvalidTokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Token no válido."})

        except get_user_model().DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "No se encontró el usuario asociado al token."})

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e), "message": "No se pudo actualizar la contraseña."})

    