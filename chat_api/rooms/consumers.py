import json
import time


from channels.generic.websocket import WebsocketConsumer
from django.core.exceptions import ValidationError


class chatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        # Enviar un mensaje de bienvenida
        self.send(text_data=json.dumps({
            'type': 'connect',
            'message': 'Socket conectado'
        }))

    def disconnect(self, close_code):
        # Enviar un mensaje de despedidaA
        self.send(text_data=json.dumps({
            'type': 'disconnect',
            'message': 'Socket desconectado!'
        }))
        
        self.close()
        
            

    def receive(self, text_data):
        pass