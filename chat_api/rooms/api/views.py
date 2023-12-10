from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rooms.api.serializers import RoomSerializer, registerRoomSerializer
from rooms.api.permissions import RoomPermission
from rooms.models import Room
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.db.models.deletion import ProtectedError
from django.http import Http404

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


    def delete(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)

        if request.user == room.user or request.user.role == 'Admin':
            try:
                room.delete()
                return Response({"message": "La sala se eliminó con éxito."}, status=status.HTTP_200_OK)
            except ProtectedError:
                return Response({"message": "No puedes eliminar la sala porque tiene participantes."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": f"Error al eliminar la sala: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": "No tienes permisos para eliminar esta sala."}, status=status.HTTP_403_FORBIDDEN)

class RoomParticipateApiView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['put', 'patch', 'delete', 'post']

    def post(self, request, room_id):  # Ajusta el nombre del argumento a 'room_id'
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise Http404("La sala no existe.")

        # Verificar si el usuario no es el propietario y no es un administrador
        if request.user != room.user and request.user.role != 'Admin':
            # Verificar si el usuario ya es un participante en la sala
            if not room.users.filter(id=request.user.id).exists():
                # Agregar al usuario como participante
                room.users.add(request.user)
                return Response({"message": "Te has unido a la sala correctamente."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Ya eres un participante en esta sala."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "No puedes unirte a tu propia sala o como administrador."}, status=status.HTTP_403_FORBIDDEN)
        
        
class getRooms(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class LeaveRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        user = request.user

        # Verificar si el usuario es un participante en la sala
        if room.users.filter(id=user.id).exists():
            # Remover al usuario de la sala
            room.users.remove(user)
            serializer = RoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No eres un participante en esta sala."}, status=status.HTTP_400_BAD_REQUEST)