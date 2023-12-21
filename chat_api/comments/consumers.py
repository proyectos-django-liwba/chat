import json
from .models import Room
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room


# consumer 2
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Se ejecuta cuando se establece la conexión.
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        
        self.close()

    async def receive(self, text_data):
    
        data = json.loads(text_data)
    
        # Hacer algo con el mensaje, si es necesario.

    async def send_user_count(self, user_count):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_count',
                'user_count': user_count
            }
        )
    
    @property
    def room_group_name(self):
        # Construct the group name for the room
        return f"chat_{self.room_id}"


