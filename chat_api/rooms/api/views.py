from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rooms.api.serializers import RoomSerializer, RegisterRoomSerializer,RoomPreviewSerializer
from rooms.api.permissions import RoomPermission
from rooms.models import Room
from django.shortcuts import get_object_or_404
from django.db.models.deletion import ProtectedError
from django.db import IntegrityError
from django.db import transaction
from django.http import Http404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Q
from notification.api.views import create_and_save_notification
from notification.models import Notification
class RoomApiView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def post(self, request):
        serializer = RegisterRoomSerializer(data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                user = request.user
                
                #se crea una funcion atomica por si ocurre un error en la creacion de la sala no se guarde nada
                with transaction.atomic():
                    # Verificar si ya existe una sala con el mismo nombre
                    if Room.objects.filter(name=serializer.validated_data['name']).exists():
                        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Ya existe una sala con este nombre."})

                    # Verificar si el usuario tiene más de 3 salas
                    if Room.objects.filter(user_id=user, is_active=True).count() >= 3:
                        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "El usuario ya tiene el máximo permitido de salas."})

                    # Crear la sala y añadir al usuario como seguidor
                    room = Room.objects.create(
                        user_id=user,
                        name=serializer.validated_data['name'],
                        description=serializer.validated_data['description'],
                        image=serializer.validated_data['image'],
                        is_active=True,
                        user_count=0,
                    )

                    
                    channel_layer = get_channel_layer()
                    group_name = "sala_group"  # Nombre del grupo WebSocket
                    event = {
                        "type": "recibir",
                        "room": RoomSerializer(room).data,  # Reemplaza con los datos de tu sala
                        "action": "create",  # Indica que se ha creado una sala nueva
                    }
                    async_to_sync(channel_layer.group_send)(group_name, event)

                return Response(status=status.HTTP_201_CREATED, data={"message": "Sala creada correctamente"})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Faltan datos"})

        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Ocurrió un error al crear la sala."})
        
        
    #obtener todas las salas del usuario
    
    def get(self, request):
        user = request.user
        rooms = Room.objects.filter(user_id=user, is_active=True)
        serializer = RoomSerializer(rooms, many=True)
        return Response({"Rooms": serializer.data}, status=status.HTTP_200_OK)
        

        

class RoomApiViewId(APIView):
    permission_classes = [RoomPermission]
    http_method_names = ['put', 'patch', 'delete']

    def put(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        
        # Verificar si el usuario autenticado es el propietario de la sala o un administrador
        if request.user == room.user_id or request.user.role == 'Admin':
            serializer = RegisterRoomSerializer(room, data=request.data)

            if serializer.is_valid(raise_exception=True):
                try:
                    serializer.save()
                    description = f"La sala '{room.name}' ha sido editada por {request.user.username}."
                    create_and_save_notification(description, room, room.followers.all(), 1, request.user, "update")


                    channel_layer = get_channel_layer()
                    group_name = "sala_group"  # Nombre del grupo WebSocket
                    event = {
                        "type": "recibir",
                        "room": RegisterRoomSerializer(room).data,  # Reemplaza con los datos de tu sala
                        "action": "update",  # Indica que se ha creado una sala nueva
                    }
                    async_to_sync(channel_layer.group_send)(group_name, event)
                    return Response({"message": "Sala actualizada correctamente"}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({"message": f"Error al actualizar la sala: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "No tienes permisos para actualizar esta sala."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)

        if request.user == room.user_id or request.user.role == 'Admin':
            try:
                if room.user_count != 0:
                    return Response({"error": "No puedes eliminar la sala porque tiene participantes."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    
                    channel_layer = get_channel_layer()
                    group_name = "sala_group"  # Nombre del grupo WebSocket
                    event = {
                        "type": "recibir",
                        "room": RegisterRoomSerializer(room).data,  # Reemplaza con los datos de tu sala
                        "action": "delete",  # Indica que se ha creado una sala nueva
                    }
                    async_to_sync(channel_layer.group_send)(group_name, event)
                    description = f"La sala '{room.name}' ha sido eliminada por {request.user.username}."
                    create_and_save_notification(description, room, room.followers.all(), 2, request.user, "delete")
                    
                    room.is_active = False
                    room.save()
                    return Response({"message": "La sala se eliminó con éxito."}, status=status.HTTP_200_OK)
            except ProtectedError:
                return Response({"message": "No puedes eliminar la sala porque tiene participantes."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": f"Error al eliminar la sala: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": "No tienes permisos para eliminar esta sala."}, status=status.HTTP_403_FORBIDDEN)


        
#obtener todas las salas activas      
class getRooms(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self, request):
        user = request.user
        rooms = Room.objects.filter(is_active=True)
        serializer = RoomPreviewSerializer(rooms, many=True)
        return Response({"Rooms": serializer.data}, status=status.HTTP_200_OK)
    
#obtener una sala por id
class getRoomById(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self, request, room_id):
        user = request.user
        room = Room.objects.get(id=room_id, is_active=True)
        is_follow = room.followers.filter(id=user.id).exists()

        # Agregar la información de seguimiento al objeto serializado
        serializer = RoomSerializer(room)
        serialized_data = serializer.data
        serialized_data['IsFollow'] = is_follow

        return Response({"Room": serialized_data}, status=status.HTTP_200_OK)
    
#obtener todas las salas en las que participa el usuario
class getRoomsFollow(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self, request):
        user = request.user
        
        # Filtra las salas en las que el usuario es seguidor
        rooms_followed = Room.objects.filter(followers=user, is_active=True)
        
        # Excluye las salas que el usuario ha creado
        rooms_participated = rooms_followed.exclude(user_id=user)
        
        serializer = RoomSerializer(rooms_participated, many=True)
        return Response({"Rooms": serializer.data}, status=status.HTTP_200_OK)

    
class RoomFollowApiView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['put', 'patch', 'delete', 'post']

    def post(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise Http404("La sala no existe.")

        # Verificar si el usuario no es el propietario y no es un administrador
        if request.user != room.user_id and request.user.role != 'Admin':
            # Verificar si el usuario ya es un participante en la sala
            if not room.followers.filter(id=request.user.id).exists():
                # Agregar al usuario como participante
                room.followers.add(request.user)
                room.save()
                return Response({"message": "Te has unido a la sala correctamente."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Ya eres un participante en esta sala."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "No puedes unirte a tu propia sala o como administrador."}, status=status.HTTP_403_FORBIDDEN)
        
    
    def delete(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        user = request.user

        # Verificar si el usuario es un participante en la sala
        if room.followers.filter(id=user.id).exists():
            # Remover al usuario de la sala

            room.followers.remove(user)
            room.save()
            serializer = RoomSerializer(room)
            return Response({"message": "Has dejado de ser participante de la sala."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No eres un participante de esta sala."}, status=status.HTTP_400_BAD_REQUEST)