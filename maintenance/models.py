from django.db import models
from hotels.models import Hotel, Room
from staff.models import Staff
import uuid

class MaintenanceIssue(models.Model):
    """Maintenance issue tracking model"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    CATEGORY_CHOICES = [
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('hvac', 'HVAC'),
        ('furniture', 'Furniture'),
        ('appliance', 'Appliance'),
        ('structural', 'Structural'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='maintenance_issues')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='maintenance_issues', blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    reported_by = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='reported_issues')
    assigned_to = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='assigned_issues', blank=True, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', '-reported_at']
    
    def __str__(self):
        return f"{self.title} - {self.property.name}"