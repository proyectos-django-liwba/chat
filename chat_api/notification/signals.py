# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from notification.models import Notification

@receiver(post_save, sender=Notification)
def notificacion_creada(sender, instance, **kwargs):
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()

    room_id = instance.room_id
    group_name = f"notifications{room_id}"
    notifications_data = Notification.objects.filter(room_id=room_id)
    
    event = {
        "type": "actualizacion_sala",
        "Notification": notifications_data,
        "action": "create",
    }

    async_to_sync(channel_layer.group_send)(group_name, event)
