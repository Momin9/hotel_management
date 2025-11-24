from django.contrib import admin
from django.utils.html import format_html
from .models import HousekeepingTask

@admin.register(HousekeepingTask)
class HousekeepingTaskAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'task_type', 'priority', 'status', 'created_at']
    list_filter = ['task_type', 'priority', 'status', 'created_at']
    search_fields = ['room__room_number', 'description']
    
    def room_number(self, obj):
        return obj.room.room_number if obj.room else "No Room"
    room_number.short_description = 'Room'
    
