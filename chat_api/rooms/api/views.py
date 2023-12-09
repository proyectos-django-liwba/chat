from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rooms.api.serializers import RoomSerializer, registerRoomSerializer
from rooms.api.permissions import RoomPermission
from rooms.models import Room
from django.shortcuts import get_object_or_404

class RegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = registerRoomSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            try:
                room = Room.objects.create(
                    name=serializer.validated_data['name'],
                    description=serializer.validated_data['description'],
                    user=user
                )
                room.users.add(user)
                # Otra lógica que desees implementar...
                return Response(status=status.HTTP_201_CREATED, data={"message": "Sala creada correctamente"})
            except Exception as e:
                return Response({"message": f"Error al crear la sala: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class RoomApiView(APIView):
    permission_classes = [RoomPermission]
    http_method_names = ['put', 'patch', 'delete']

    def put(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        
        # Verificar si el usuario autenticado es el propietario de la sala o un administrador
        if request.user == room.user or request.user.role == 'Admin':
            serializer = RoomSerializer(room, data=request.data)

            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response({"message": "Sala actualizada correctamente"}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({"message": f"Error al actualizar la sala: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "No tienes permisos para actualizar esta sala."}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        serializer = RoomSerializer(room, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data={"message": "Sala actualizada correctamente"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        
        if request.user == room.user or request.user.role == 'Admin':
            try:
                room.delete()
                return Response({"message": "La sala se eliminó con éxito."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"message": f"Error al eliminar la sala: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "No tienes permisos para eliminar esta sala."}, status=status.HTTP_403_FORBIDDEN)

class RoomParticipateApiView(APIView):
    permission_classes = [RoomPermission]
    http_method_names = ['put', 'patch', 'delete']

    def leave_room(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        user = request.user

        # Verificar si el usuario es un participante en la sala
        if room.users.filter(id=user.id).exists():
            # Remover al usuario de la sala
            room.users.remove(user)
            return Response({"detail": "Te has salido de la sala."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No eres un participante en esta sala."}, status=status.HTTP_400_BAD_REQUEST)