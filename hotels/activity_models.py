from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

class RoomActivityLog(models.Model):
    """Track all room-related activities and changes"""
    
    ACTION_CHOICES = [
        ('status_change', 'Status Changed'),
        ('assignment', 'Staff Assignment'),
        ('maintenance_request', 'Maintenance Request'),
        ('cleaning_completed', 'Cleaning Completed'),
        ('inspection', 'Room Inspection'),
        ('note_added', 'Note Added'),
        ('price_change', 'Price Updated'),
        ('amenity_change', 'Amenities Updated'),
        ('guest_checkin', 'Guest Check-in'),
        ('guest_checkout', 'Guest Check-out'),
        ('payment_received', 'Payment Received'),
        ('reservation_created', 'Reservation Created'),
        ('reservation_cancelled', 'Reservation Cancelled'),
        ('housekeeping_assigned', 'Housekeeping Assigned'),
        ('other', 'Other'),
    ]
    
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    
    # Store old and new values for tracking changes
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    
    # Additional context data (JSON field for flexibility)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Room Activity Log'
        verbose_name_plural = 'Room Activity Logs'
    
    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'System'
        return f"{user_name} - {self.get_action_display()} - Room {self.room.room_number}"
    
    @classmethod
    def log_activity(cls, room, user, action, description, old_value=None, new_value=None, **metadata):
        """Helper method to create activity logs"""
        return cls.objects.create(
            room=room,
            user=user,
            action=action,
            description=description,
            old_value=old_value,
            new_value=new_value,
            metadata=metadata
        )
    
    def get_time_ago(self):
        """Get human readable time difference"""
        from django.utils.timesince import timesince
        return timesince(self.created_at)
    
    def get_user_display(self):
        """Get user display name with role"""
        if not self.user:
            return 'System'
        
        name = self.user.get_full_name() or self.user.username
        role = getattr(self.user, 'role', None)
        if role:
            return f"{name} ({role})"
        return name