from django.db import models
from hotels.models import Room
from staff.models import Staff
import uuid

class HousekeepingTask(models.Model):
    """Housekeeping task model for room cleaning and maintenance"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('checkout_cleaning', 'Checkout Cleaning'),
        ('maintenance_cleaning', 'Maintenance Cleaning'),
        ('deep_cleaning', 'Deep Cleaning'),
        ('inspection', 'Inspection'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='housekeeping_tasks')
    assigned_staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='housekeeping_tasks', null=True, blank=True)
    task_type = models.CharField(max_length=30, choices=TASK_TYPE_CHOICES, default='checkout_cleaning')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.PositiveIntegerField(default=1)  # 1=low, 5=high
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', 'created_at']
    
    def __str__(self):
        return f"Task {self.task_type} - Room {self.room.room_number}"