import json

from channels.db import database_sync_to_async
# manejo de datos
from .models import Room
from rooms.api.serializers import RoomSerializer
# respuestas
from rest_framework import status
from rest_framework.response import Response
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Room
""" class chatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
        # Enviar un mensaje de bienvenida
        await self.send(text_data=json.dumps({
            'type': 'connect',
            'message': 'Socket conectado',
            'user_count': await self.send_user_count()
        }))

    async def disconnect(self, close_code):
        await self.send(text_data=json.dumps({
            'type': 'disconnect',
            'message': 'Socket desconectado'
        }))
        
        # Obtener el ID de la sala desde la URL
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        print(f"ID de la sala recibido: {self.room_id}")
        
        await self.decrement_user_count( self.room_id )
        print(f"Usuario desagregado a la sala {self.room_id}")
        
        await self.close()
        

    async def receive(self, text_data):
        data = json.loads(text_data)
         
        if data.get("type") == 'init':
            # Obtener el ID de la sala 
            room_id = data.get('room_id')

            print(f"ID de la sala recibido: {room_id}")
            
            await self.increment_user_count(room_id)

            # Puedes enviar una respuesta de vuelta 
            await self.send(text_data=json.dumps({
                'type': 'init_ack',
                'message': f'ID de sala {room_id} recibido con éxito.',
                'user_count': await self.send_user_count()
            }))
            
    
    
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

    @database_sync_to_async
    def send_user_count(self):
        try:
            # Obtener el ID de la sala desde la URL
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            room_query = Room.objects.filter(id=self.room_id)
            room = room_query.first()

            return room.user_count
                   
        except Room.DoesNotExist:
            print(f"La sala con ID {self.room_id} no existe.")
        except Exception as e:
            print(f"Error al obtener user_count: {e}") """
            

# consumers.py



class chatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Se ejecuta cuando se establece la conexión.
        await self.accept()

        # Incrementa el contador de usuarios al conectarse.
        await self.update_user_count(1)

    async def disconnect(self, close_code):
        # Se ejecuta cuando se cierra la conexión.
        await self.update_user_count(-1)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data['message']
            # Hacer algo con el mensaje, si es necesario.
        except KeyError:
            # Manejar la falta de la clave 'message' en el diccionario.
            message = None


        # Hacer algo con el mensaje, si es necesario.

    @sync_to_async
    def update_user_count(self, increment):
        # Actualiza el contador de usuarios en la base de datos.
        room_id = self.scope['url_route']['kwargs']['room_id']
        room = Room.objects.get(id=room_id)
        room.user_count += increment
        room.save()

        # Envía la nueva cantidad de usuarios a todos los clientes conectados.
        self.send_user_count(room.user_count)

    async def send_user_count(self, user_count):
        # Envía la cantidad de usuarios a todos los clientes conectados.
        await self.send(text_data=json.dumps({'user_count': user_count}))
