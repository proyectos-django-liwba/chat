from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rooms.api.serializers import RoomSerializer, RegisterRoomSerializer
from rooms.api.permissions import RoomPermission
from rooms.models import Room
from django.shortcuts import get_object_or_404
from django.db.models.deletion import ProtectedError
from django.db import IntegrityError
from django.db import transaction
from django.core.paginator import Paginator
from django.http import Http404
class RegisterView(APIView):
    permission_classes = [IsAuthenticated]

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
                    if Room.objects.filter(user_id=user).count() >= 3:
                        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "El usuario ya tiene el máximo permitido de salas."})

                    # Crear la sala y añadir al usuario como seguidor
                    room = Room.objects.create(
                        user_id=user,
                        name=serializer.validated_data['name'],
                        description=serializer.validated_data['description'],
                        image=serializer.validated_data['image'],
                        is_active=True,
                        user_count=1,
                    )
                    room.followers.add(user)

                return Response(status=status.HTTP_201_CREATED, data={"message": "Sala creada correctamente"})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Faltan datos"})

        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Ocurrió un error al crear la sala."})
        
    def get(self, request):
        serializer = RoomSerializer(data=request.data)
        

class RoomApiView(APIView):
    permission_classes = [RoomPermission]
    http_method_names = ['put', 'patch', 'delete']

    def put(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)

        # Verificar si el usuario autenticado es el propietario de la sala o un administrador
        if request.user == room.user_id or request.user.role == 'Admin':
            serializer = RoomSerializer(room, data=request.data)

            if serializer.is_valid(raise_exception=True):
                try:
                    serializer.save()
                    return Response({"message": "Sala actualizada correctamente"}, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({"message": f"Error al actualizar la sala: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "No tienes permisos para actualizar esta sala."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)

        if request.user == room.user_id or request.user.role == 'Admin':
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

    def post(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise Http404("La sala no existe.")

        # Verificar si el usuario no es el propietario y no es un administrador
        if request.user != room.user_id and request.user.role != 'Admin':
            # Verificar si el usuario ya es un participante en la sala
            if not room.followers.filter(id=request.user.id).exists():
                room.user_count += 1
                # Agregar al usuario como participante
                room.followers.add(request.user)
                room.save()
                return Response({"message": "Te has unido a la sala correctamente."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Ya eres un participante en esta sala."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "No puedes unirte a tu propia sala o como administrador."}, status=status.HTTP_403_FORBIDDEN)
        
        
class getRooms(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get(self, request):
        user = request.user
        rooms = Room.objects.filter(is_active=True)
        page_size = 10
        paginator = Paginator(rooms, page_size)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        serializer = RoomSerializer(page_obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

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