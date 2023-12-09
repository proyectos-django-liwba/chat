from django.contrib import admin
from rooms.models import Room

# Register your models here.
admin.site.register(Room)

class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
