from django.db import models
from django.conf import settings
from hotels.models import Hotel
import uuid

class Report(models.Model):
    """Report generation and storage"""
    TYPE_CHOICES = [
        ('occupancy', 'Occupancy Report'),
        ('revenue', 'Revenue Report'),
        ('adr', 'Average Daily Rate'),
        ('revpar', 'Revenue Per Available Room'),
        ('housekeeping', 'Housekeeping Performance'),
        ('maintenance', 'Maintenance Report'),
        ('guest_satisfaction', 'Guest Satisfaction'),
        ('financial', 'Financial Summary'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    property = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generated_reports')
    date_from = models.DateField()
    date_to = models.DateField()
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.FileField(upload_to='reports/', blank=True, null=True)
    parameters = models.JSONField(default=dict)  # Store report parameters
    data = models.JSONField(default=dict)  # Store report data
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.type}"

class Dashboard(models.Model):
    """Custom dashboard configurations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboards')
    property = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='dashboards', null=True, blank=True)
    widgets = models.JSONField(default=list)  # Store widget configurations
    layout = models.JSONField(default=dict)  # Store layout settings
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Metric(models.Model):
    """Store calculated metrics for reporting"""
    METRIC_TYPE_CHOICES = [
        ('occupancy_rate', 'Occupancy Rate'),
        ('adr', 'Average Daily Rate'),
        ('revpar', 'Revenue Per Available Room'),
        ('total_revenue', 'Total Revenue'),
        ('guest_satisfaction', 'Guest Satisfaction'),
        ('housekeeping_efficiency', 'Housekeeping Efficiency'),
        ('maintenance_response_time', 'Maintenance Response Time'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='metrics')
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPE_CHOICES)
    value = models.DecimalField(max_digits=15, decimal_places=4)
    date = models.DateField()
    metadata = models.JSONField(default=dict)  # Additional metric data
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['property', 'metric_type', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.metric_type} - {self.value} ({self.date})"