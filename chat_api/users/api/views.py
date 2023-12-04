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
from users.models import User
""" from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from users.api.serializers import UserRegisterSerializer, UserSerializer, UserUpdateSerializer
from rest_framework.permissions import IsAuthenticated """
# Create your views here.

class RegisterView(APIView):
  #endpoint para registrar usuarios
    def post(self, request):
      # leer los datos del request
      serializer = UserRegisterSerializer(data=request.data)
      # validar los datos
      if serializer.is_valid(raise_exception=True):
        # guardar
        serializer.save()
        return Response(status=status.HTTP_201_CREATED, data={"message":"Usuario creado correctamente", "user":serializer.data})
      
      return Response(status=status.HTTP_400_BAD_REQUEST, data={"error":serializer.errors, "message":"No se pudo crear el usuario"})
    
  
class UserView(APIView):
  # seguridad para el endpoint, solo usuarios autenticados
  permission_classes = [IsAuthenticated]
  
  # obtener el usuario autenticado, se debe agregar un header con el token, "bearer <token>"
  def get(self, request):
    serializer = UserSerializer(request.user)
    
    # validar los datos
    if serializer is not None:
      # retornar los datos del usuario
      return Response(status=status.HTTP_200_OK, data={"user":serializer.data})
    
    return Response(status=status.HTTP_400_BAD_REQUEST, data={"error":serializer.errors, "message":"El token es inválido"})
  
  # actualizar usuario autenticado
  def put(self, request):
    # obtener datos del usuario autenticado
    user = User.objects.get(id=request.user.id)
    # se agregan los nuevos datos y los datos anteriores
    serializer = UserUpdateSerializer(user, request.data)
    
    # validar los datos
    if serializer.is_valid(raise_exception=True):
      # guardar
      serializer.save()
      return Response(status=status.HTTP_200_OK, data={"message":"Usuario actualizado correctamente", "user":serializer.data})
    
    return Response(status=status.HTTP_400_BAD_REQUEST, data={"error":serializer.errors, "message":"No se pudo actualizar el usuario"})
  
class UserChangePasswordView(APIView):
  
  # seguridad para el endpoint, solo usuarios autenticados
  permission_classes = [IsAuthenticated]
  
  # actualizar usuario autenticado
  def put(self, request):
    # obtener datos del usuario autenticado
    user = User.objects.get(id=request.user.id)
    # se agregan los nuevos datos y los datos anteriores
    serializer = UserChangePasswordSerializer(user, request.data)
    
    # validar los datos
    if serializer.is_valid(raise_exception=True):
      # guardar
      serializer.save()
      return Response(status=status.HTTP_200_OK, data={"message":"Contraseña actualizada correctamente", "user":serializer.data})
    
    return Response(status=status.HTTP_400_BAD_REQUEST, data={"error":serializer.errors, "message":"No se pudo actualizar la contraseña"}) 

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

# Elmer    
    
""" class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data = serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserView(APIView):
    def get(self, request):
        perimission_classes = [IsAuthenticated]
        
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = UserUpdateSerializer(user, request.data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data = serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) """
      
