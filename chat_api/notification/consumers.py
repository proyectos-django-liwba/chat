import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("WebSocket conectado")
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        

        await self.channel_layer.group_add(
            self.room_group_name,  
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def enviar_actualizacion_sala(self, event):
        message = {
            'type': 'actualizacion_sala',
            'Notification': event['Notification'],
            'action': event['action'],
        }
        await self.send(text_data=json.dumps(message))


    async def recibir(self, event):
        print("Recibido un evento WebSocket")
        if 'Notification' in event and 'action' in event:
            await self.enviar_actualizacion_sala(event)
            
            
    @property
    def room_group_name(self):
        # Construct the group name for the room
        return f"notifications{self.room_id}"
