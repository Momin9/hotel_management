from django.db import models
from django.conf import settings
from hotels.models import Room
import uuid

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