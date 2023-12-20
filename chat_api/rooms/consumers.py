import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.db import database_sync_to_async
# manejo de datos
from .models import Room
from rooms.api.serializers import RoomSerializer
# respuestas
from rest_framework import status
from rest_framework.response import Response

class chatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        # Enviar un mensaje de bienvenida
        await self.send(text_data=json.dumps({
            'type': 'connect',
            'message': 'Socket conectado'
        }))

    async def disconnect(self, close_code):
        await self.close()
        

    async def receive(self, text_data):
        data = json.loads(text_data)
         
        if data.get("type") == 'init':
            # Obtener el ID de la sala desde el mensaje de inicialización
            room_id = data.get('room_id')

            # Ahora puedes usar room_id como lo necesites en tu lógica
            print(f"ID de la sala recibido: {room_id}")

            # Puedes enviar una respuesta de vuelta si es necesario
            await self.send(text_data=json.dumps({
                'type': 'init_ack',
                'message': f'ID de sala {room_id} recibido con éxito.'
            }))
            
            await self.increment_user_count(room_id)
        
        if data.get("type") == 'close':
            # Obtener el ID de la sala desde el mensaje de inicialización
            room_id = data.get('room_id')
            
            # Ahora puedes usar room_id como lo necesites en tu lógica
            print(f"ID de la sala recibido: {room_id}")
            
            await self.send(text_data=json.dumps({
                'type': 'close_ack',
                'message': f'ID de sala {room_id} recibido con éxito.'
            }))
            
            await self.decrement_user_count(room_id)
    
    @database_sync_to_async
    def increment_user_count(self, room_id):
        try:
            room_query = Room.objects.filter(id=room_id)
            room = room_query.first()

            if room:
                # Incrementar el contador de usuarios
                room.user_count += 1
                room.save()
                print(f"Usuario agregado a la sala {room_id}")
                
        except Room.DoesNotExist:
            print(f"La sala con ID {room_id} no existe.")
        except Exception as e:
            print(f"Error al incrementar user_count: {e}")

    @database_sync_to_async
    def decrement_user_count(self, room_id):
        try:
            room_query = Room.objects.filter(id=room_id)
            room = room_query.first()

            if room:
                # Incrementar el contador de usuarios
                room.user_count -= 1
                room.save()
                print(f"Usuario desagregado a la sala {room_id}")
                
        except Room.DoesNotExist:
            print(f"La sala con ID {room_id} no existe.")
        except Exception as e:
            print(f"Error al decrementar user_count: {e}")

    async def send_user_count(self):
        room = await database_sync_to_async(Room.objects.get)(id=self.room_id)
        # Emitir el evento a través del grupo de la sala
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_users_count',
                'user_count': room.user_count,
            }
        )

    async def update_users_count(self, event):
        # Enviar el mensaje actualizado a través del WebSocket
        await self.send(text_data=event['user_count'])