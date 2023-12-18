from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rooms.api.serializers import RoomSerializer, RegisterRoomSerializer,RoomPreviewSerializer
from rooms.api.permissions import RoomPermission
from rooms.models import Room
from django.shortcuts import get_object_or_404
from django.db.models.deletion import ProtectedError
from django.db import transaction
from django.http import Http404
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from users.models import User
from rest_framework.decorators import action
class RoomViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [RoomPermission, IsAuthenticated]
    
    #obtener todas las salas activas   
    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return RoomPreviewSerializer
        return RoomPreviewSerializer
    @transaction.atomic
    def perform_create(self, serializer):
        # Obtener la instancia del usuario a partir del ID
        user_id = self.request.user.id
        user_instance = User.objects.get(id=user_id)

        # Asignar la instancia del usuario al campo user_id y a la relación followers
        serializer.validated_data['user_id'] = user_instance
        room = serializer.save()
        room.followers.add(user_instance)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Sala creada exitosamente"}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        room = self.get_object()
        if request.user != room.user_id and request.user.role != 'Admin':
            
            error_message = "Usted no tiene permiso para actualizar la sala."
            return Response({"error": error_message}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(room, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"message": "Sala Actualizada correctamente!"}, status=status.HTTP_200_OK)


    def destroy(self, request, pk=None, *args, **kwargs):
        room = self.get_object()
        if request.user != room.user_id and request.user.role != 'Admin':
            return Response({"message": "No tienes permisos para eliminar esta sala."}, status=status.HTTP_403_FORBIDDEN)
        try:
            self.perform_destroy(room)
        except ProtectedError:
            return Response({"message": "No puedes eliminar la sala porque tiene participantes."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "La sala se eliminó con éxito."}, status=status.HTTP_200_OK)


class RoomGetViewSet(ReadOnlyModelViewSet):
    http_method_names = ['get']
    serializer_class = RoomPreviewSerializer 
    def get_queryset(self):
        # Filtrar las salas que estén activas
        return Room.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        # Obtener todas las salas activas con información limitada
        queryset = self.get_queryset()
        serializer = RoomPreviewSerializer(queryset, many=True)
        return Response({"Rooms": serializer.data}, status=status.HTTP_200_OK)


    def retrieve(self, request, pk=None):
        # Obtener toda la información de una sala por su ID
        room = self.get_object()
        serializer = RoomSerializer(room)
        return Response({"Rooms": serializer.data}, status=status.HTTP_200_OK)

class RoomFollowerViewSet(ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Room.objects.filter(followers=user)

    @action(detail=False, methods=['post'])
    def join(self, request):
        room_id = request.data.get('room_id')

        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            try:
                room = Room.objects.get(pk=room_id)
            except Room.DoesNotExist:
                return Response({"message": "La sala no existe."}, status=status.HTTP_404_NOT_FOUND)

            # Verificar si el usuario no es el propietario y no es un administrador
            if request.user != room.user_id and request.user.role != 'Admin':
                # Verificar si el usuario ya es un participante en la sala
                if not room.followers.filter(id=request.user.id).exists():
                    room.user_count += 1
                    # Agregar al usuario como participante
                    room.followers.add(request.user)
                    room.save()
                    serializer = self.get_serializer(room)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Ya eres un participante en esta sala."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "No puedes unirte a tu propia sala o como administrador."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Debes iniciar sesión para unirte a esta sala."}, status=status.HTTP_401_UNAUTHORIZED)


    @action(detail=True, methods=['delete'])
    def leave(self, request, pk=None):
        room = self.get_object()
        user = request.user

        # Verificar si el usuario es un participante en la sala
        if room.followers.filter(id=user.id).exists():
            # Remover al usuario de la sala
            room.user_count -= 1
            room.followers.remove(user)
            room.save()
            serializer = self.get_serializer(room)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No eres un participante de esta sala."}, status=status.HTTP_400_BAD_REQUEST)
#obtener todas las salas en las que participa el usuario
class getRoomsParticipe(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self, request):
        user = request.user
        rooms_participated = Room.objects.filter(followers=user)
        serializer = RoomSerializer(rooms_participated, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class LeaveRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        user = request.user

        # Verificar si el usuario es un participante en la sala
        if room.followers.filter(id=user.id).exists():
            # Remover al usuario de la sala
            room.user_count -= 1
            room.followers.remove(user)
            room.save()
            serializer = RoomSerializer(room)
            return Response({"message": "Has dejado de ser participante de la sala."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No eres un participante de esta sala."}, status=status.HTTP_400_BAD_REQUEST)
        
