from django.db import models
from hotels.models import Room
from staff.models import Staff
from django.conf import settings
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

class HousekeepingSchedule(models.Model):
    """Housekeeping schedule model"""
    SHIFT_CHOICES = [
        ('morning', 'Morning (6AM - 2PM)'),
        ('afternoon', 'Afternoon (2PM - 10PM)'),
        ('night', 'Night (10PM - 6AM)'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='housekeeping_schedules')
    date = models.DateField()
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    rooms = models.ManyToManyField(Room, blank=True, related_name='scheduled_cleanings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_schedules')
    
    class Meta:
        unique_together = ['staff', 'date', 'shift']
        ordering = ['date', 'shift']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.date} ({self.get_shift_display()})"