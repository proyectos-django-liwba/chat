import json
import time

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.exceptions import ValidationError


class ProgressBarConsumer(WebsocketConsumer):
        def connect(self):
            self.accept()

            # Enviar un mensaje de bienvenida
            self.send(text_data=json.dumps({
                'type': 'connect',
                'message': 'Hola, mundo!'
            }))

        def disconnect(self, close_code):
            pass

        def receive(self, text_data):
            pass