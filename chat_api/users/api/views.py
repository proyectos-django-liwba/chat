from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.api.serializers import (
  UserRegisterSerializer,
  UserSerializer, 
  UserUpdateSerializer,
  UserChangePasswordSerializer,
  VerificarCuentaSerializer,
)
from django.shortcuts import redirect
import jwt
from django.conf import settings
from users.models import User
from datetime import datetime
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from users.api.permissions import IsOwner
from rest_framework.exceptions import PermissionDenied

class CustomTokenObtainPairView(TokenObtainPairView):
    #definir que petición se puede hacer a este endpoint
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

                # Serializar y agregar los detalles del usuario a la respuesta del token
                user_serializer = UserSerializer(user)
                user_data = user_serializer.data

                # Crear un nuevo diccionario de respuesta con el orden deseado
                new_response_data = {'user': user_data, 'access': response.data['access'], 'refresh': response.data['refresh']}
                
                # Devolver la respuesta con el nuevo orden
                return Response(new_response_data, status=response.status_code)
              
        except Exception as e:
            # Personalizar la respuesta en caso de un error
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Ocurrió un error al verificar las credenciales"})

        # Si no hay un error y la respuesta es exitosa, devolver la respuesta original
        return response


class RegisterView(APIView):
    #definir que petición se puede hacer a este endpoint
    http_method_names = ['post']

    #endpoint para registrar usuarios
    def post(self,  request, *args, **kwargs):
        # leer los datos del request
        serializer = UserRegisterSerializer(data=request.data)
        
        # validar los datos
        if serializer.is_valid(raise_exception=True):
          # guardar
          serializer.save()
          # respuesta en caso de exito
          return Response(status=status.HTTP_201_CREATED, data={"message":"Usuario creado correctamente"})
        
        # respuesta en caso de error
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error":serializer.errors, "message":"No se pudo crear el usuario"})

  
class UserView(APIView):
  # seguridad para el endpoint, solo usuarios autenticados
  permission_classes = [IsOwner]
  
  #definir que petición se puede hacer a este endpoint
  http_method_names = ['put', 'delete']

  # actualizar usuario autenticado
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
        user.is_active = False
        user.save()

        return Response(
            {"message": "Usuario desactivado correctamente"},
            status=status.HTTP_204_NO_CONTENT
        )
    except PermissionDenied as e:
        # Manejar la excepción de permiso denegado
        return Response(status=status.HTTP_403_FORBIDDEN, data={"error": str(e)})  
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "Usuario no encontrado"})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "No se pudo desactivar el usuario"})

# falta revisar estos endpoints y crear los del admin         
class UserChangePasswordView(APIView):
  # seguridad para el endpoint, solo usuarios autenticados
  permission_classes = [IsAuthenticated]
  
  #definir que petición se puede hacer a este endpoint
  http_method_names = ['put']
  
  
  # actualizar usuario autenticado
  def put(self, request, *args, **kwargs):
    try:
      response = super().post(request, *args, **kwargs)
      # obtener datos del usuario autenticado
      user = User.objects.get(id=request.user.id)
      # se agregan los nuevos datos y los datos anteriores
      serializer = UserChangePasswordSerializer(user, request.data)
      
      # validar los datos
      if serializer.is_valid(raise_exception=True):
        # guardar
        serializer.save()
        return Response(status=status.HTTP_200_OK, data={"message":"Contraseña actualizada correctamente", "user":serializer.data})
    except Exception as e:
      return Response(status=status.HTTP_400_BAD_REQUEST, data={"error":serializer.errors, "message":"No se pudo actualizar la contraseña"}) 
    return response
  
class VerificarOTP(APIView):
  def post(self, request):
      try:
          data = request.data
          serializers = VerificarCuentaSerializer(data = data)
          
          if serializers.is_valid():
              email = serializers.data['email']
              otp = serializers.data['otp']
              
              user = User.objects.filter(email = email)
              if not user.exists():
                  return Response({
                      'status': 400,
                      'message': 'correo no encontrado',
                      'data': 'correo invalido'
                      })
              
              if user[0].otp != otp:

                  return Response({
                      'status': 200,
                      'message': 'Algo salio mal',
                      'data': 'Codigo invalido'
                      })
              
              user = user.first()
              user.esta_verificado = True
              user.save()
              
              return Response({
                  'status': 200,
                  'message': 'Usuario verificado',
                  'data': 'Usuario verificado'
                  })
          
          return Response({
              'status': 400,
              'message': 'Algo salio mal',
              'data': serializers.errors
              })  
      
      except Exception as e:
          print(e)

class AccountActivationView(APIView):
    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            user = User.objects.get(id=user_id)

            # Activa la cuenta o realiza otras acciones según tus necesidades
            user.is_active = True
            user.save()

            # Redirige a la URL de éxito después de la activación
            return redirect('https://tu-sitio.com/exito_activacion')
        except jwt.ExpiredSignatureError:
            return Response({'error': 'El token de activación ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({'error': 'Token de activación no válido.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

      
