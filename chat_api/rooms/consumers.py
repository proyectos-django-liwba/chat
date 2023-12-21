import json
from .models import Room
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room

# consumer 2
class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Incrementa el contador de usuarios al conectarse.
        user_count = await self.update_user_count(1)
        
        # Almacena la instancia del WebSocket
        self.websocket = self

        # Se ejecuta cuando se establece la conexión.
        await self.accept()
        
        # Después de aceptar la conexión, envía el mensaje
        try:
            await self.send_user_count(user_count)
        except Exception as e:
            print(f"Error sending user count: {e}")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Se ejecuta cuando se cierra la conexión.
        user_count = await self.update_user_count(-1)
        
        await self.send_user_count(user_count)
        
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
        
    @sync_to_async
    def update_user_count(self, increment):
        # Actualiza el contador de usuarios en la base de datos.
        room_id = self.room_id
        room = Room.objects.get(id=room_id)
        room.user_count += increment
        room.save()

        return room.user_count

    async def user_count(self, event):
        try:
            await self.send(text_data=json.dumps({'user_count': event['user_count']}))
        except Exception as e:
            print(f"Error sending user_count: {e}")


    @property
    def room_group_name(self):
        # Construct the group name for the room
        return f"chat_{self.room_id}"


# consumer 2

class UserCountConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        
        await self.accept()
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        self.close()

    async def receive(self, text_data):
        pass
    
    async def send_user_count(self, user_count):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_count',
                'user_count': user_count
            }
        )
        
    async def user_count(self, event):
        # Envía la cantidad de usuarios a todos los clientes conectados.
        await self.send(text_data=json.dumps({'user_count': event['user_count']}))
        
    @property
    def room_group_name(self):
        # Construct the group name for the room
        return f"chat_{self.room_id}"
    

class SalaConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket conectado")
        await self.channel_layer.group_add(
            'sala_group',  # Nombre del grupo WebSocket
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'sala_group',  # Nombre del grupo WebSocket
            self.channel_name
        )

    async def enviar_actualizacion_sala(self, event):
        message = {
            'type': 'actualizacion_sala',
            'room': event['room'],
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
        if 'room' in event and 'accion' in event:
            await self.enviar_actualizacion_sala(event)
