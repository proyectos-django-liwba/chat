import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from comments.models import Comment


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("WebSocket conectado")
        await self.channel_layer.group_add(
            'comments_group',  # Nombre del grupo WebSocket
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'comments_group',  # Nombre del grupo WebSocket
            self.channel_name
        )

    async def enviar_actualizacion_sala(self, event):
        message = {
            'type': 'actualizacion_sala',
            'comments': event['comments'],
            'accion': event['accion'],
        }
        await self.send(text_data=json.dumps(message))
        
    """ async def enviar_actualizacion_sala(self, event):
        message = {
            'type': 'actualizacion_sala',
            'accion': event['accion'],
        }
        await self.send(text_data=json.dumps(message)) """

    async def recibir(self, event):
        print("Recibido un evento WebSocket")
        if 'comments' in event and 'accion' in event:
            await self.enviar_actualizacion_sala(event)
