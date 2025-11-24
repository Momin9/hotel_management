from django.db import models
import uuid

class GuestProfile(models.Model):
    """Guest profile model - tenant-scoped for cross-property guest tracking"""
    LOYALTY_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    id_number = models.CharField(max_length=50, blank=True)
    preferences = models.TextField(blank=True)
    loyalty_status = models.CharField(max_length=20, choices=LOYALTY_CHOICES, default='bronze')
    loyalty_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"