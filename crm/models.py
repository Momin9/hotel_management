from django.db import models
from django_countries.fields import CountryField
import uuid

class GuestProfile(models.Model):
    """Guest profile model - tenant-scoped for cross-property guest tracking"""
    LOYALTY_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    GUEST_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('company', 'Company'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest_type = models.CharField(max_length=20, choices=GUEST_TYPE_CHOICES, default='individual')
    company = models.ForeignKey('hotels.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='guests')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = CountryField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    id_number = models.CharField(max_length=50, blank=True)
    national_id_card = models.CharField(max_length=50, unique=True, help_text="National Identity Card Number")
    national_id_card_image = models.ImageField(upload_to='national_id_cards/', blank=True, null=True, help_text="National Identity Card Image")
    google_drive_file_id = models.CharField(max_length=200, blank=True, help_text="Google Drive file ID for ID card image")
    google_drive_file_link = models.URLField(blank=True, help_text="Google Drive file view link")
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