from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from comments.models import Comment
from .serializers import CommentSerializer
from django.http import Http404
from comments.api.permissions import IsCommentCreatorOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
class CommentListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response({"Rooms": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        # Accede al usuario autenticado a través del token
        user = request.user

        # Agrega el usuario a los datos del comentario antes de la validación
        data = request.data.copy()
        data['user_id'] = user.id

        serializer = CommentSerializer(data=data)
        
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(status=status.HTTP_201_CREATED, data={"message": "Comentario creado correctamente"})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Ocurrió un error al crear el comentario."})
        

class CommentDetailAPIView(APIView):
    permission_classes = [IsCommentCreatorOrReadOnly]
    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404

    """ def get(self, request, pk):
        comment = self.get_object(pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data) """

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
                return Response(data={"message": "Comentario actualizado correctamente"})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Ocurrió un error al actualizar el comentario."})
        

    def delete(self, request, pk):
        comment = self.get_object(pk)
        try:
            comment.delete()
            return Response({"message": "El comentario se eliminó con éxito."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Error al eliminar el comentario: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
