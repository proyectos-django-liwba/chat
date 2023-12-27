from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from comments.models import Comment
from .serializers import CommentSerializer, CommentSerializerList
from django.http import Http404
from comments.api.permissions import IsCommentCreatorOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from users.api.serializers import UserSerializerUsername
from users.models import User
class CommentListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response({"Rooms": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['user_id'] = user.id
        serializer = CommentSerializer(data=data)

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                user_instance = User.objects.get(pk=user.id)
                user_info_serializer = UserSerializerUsername(user_instance)
                user_info = user_info_serializer.data

                # Combina la información del comentario y del usuario en un solo diccionario
                event_data = {**serializer.data, "user": user_info}

                room_id = data.get('room_id')
                room_group_name = f"comments_{room_id}"
                channel_layer = get_channel_layer()
                group_name = room_group_name

                event = {
                    "type": "recibir",
                    "Comment": event_data,
                    "action": "create"
                }


                # Envía el evento a través del socket
                async_to_sync(channel_layer.group_send)(group_name, event)
                return Response(status=status.HTTP_201_CREATED, data={"message": "Comentario creado correctamente"})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Ocurrió un error al crear el comentario."})
        

class CommentDetailAPIView(APIView):
    permission_classes = [IsCommentCreatorOrReadOnly]
    pagination_class = PageNumberPagination  # Utiliza la paginación por número de página
    page_size = 20
    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        # Obtén la sala específica
        room_id = pk

        # Obtiene todos los comentarios asociados a la sala con paginación
        comments = Comment.objects.filter(room_id=room_id).order_by('-id')

        # Pagina los comentarios
        paginator = self.pagination_class()
        paginated_comments = paginator.paginate_queryset(comments, request)

        # Serializa los comentarios paginados y los devuelve como respuesta
        serializer = CommentSerializerList(paginated_comments, many=True)

        return Response({"Comments": serializer.data}, status=status.HTTP_200_OK)


    def put(self, request, pk):
        comment = self.get_object(pk)
        user = request.user

        # Agrega el usuario a los datos del comentario antes de la validación
        data = request.data.copy()
        data['user_id'] = user.id

        serializer = CommentSerializer(comment, data=data)  # Pasa la instancia existente como primer argumento
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                room_id = data.get('room_id')
                room_group_name = f"comments_{room_id}"
                channel_layer = get_channel_layer()
                group_name = room_group_name
                event = {
                    "type": "recibir",
                    "Comment": CommentSerializerList(comment).data,
                    "action": "update", 
                }
                async_to_sync(channel_layer.group_send)(group_name, event)
                return Response(data={"message": "Comentario actualizado correctamente"})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Ocurrió un error al actualizar el comentario."})
        

    def delete(self, request, pk):
        comment = self.get_object(pk)
        try:
            room_id = comment.room_id.id  # Ajusta esto según la relación en tu modelo Comment
            room_group_name = f"comments_{room_id}"  # Ajusta esto según tu esquema de nombres
            channel_layer = get_channel_layer()
            group_name = room_group_name
            event = {
                "type": "recibir",
                "Comment": CommentSerializerList(comment).data,
                "action": "delete",

            }
            async_to_sync(channel_layer.group_send)(room_group_name, event)
            comment.delete()
            

            
            return Response({"message": "El comentario se eliminó con éxito."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Error al eliminar el comentario: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
