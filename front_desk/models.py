from django.db import models
from django.conf import settings
from hotels.models import Hotel, Room
from reservations.models import Reservation
from crm.models import GuestProfile
import uuid

class CheckInOut(models.Model):
    """Check-in/out operations model"""
    STATUS_CHOICES = [
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('no_show', 'No Show'),
        ('early_departure', 'Early Departure'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='checkin_record')
    guest = models.ForeignKey(GuestProfile, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    # Check-in details
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='checkins_processed')
    
    # Check-out details
    checked_out_at = models.DateTimeField(null=True, blank=True)
    checked_out_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='checkouts_processed')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='checked_in')
    
    # Additional details
    number_of_guests = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Charges and deposits
    incidental_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Check-in {self.guest.full_name} - Room {self.room.room_number}"

class WalkInReservation(models.Model):
    """Walk-in guest reservations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest = models.ForeignKey(GuestProfile, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    property = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.PositiveIntegerField(default=1)
    
    rate_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Walk-in: {self.guest.full_name} - {self.check_in_date}"

class GuestFolio(models.Model):
    """Guest folio for tracking charges and payments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checkin_record = models.OneToOneField(CheckInOut, on_delete=models.CASCADE, related_name='folio')
    guest = models.ForeignKey(GuestProfile, on_delete=models.CASCADE)
    
    # Folio details
    folio_number = models.CharField(max_length=50, unique=True)
    room_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    incidental_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payments_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    is_settled = models.BooleanField(default=False)
    settled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Folio {self.folio_number} - {self.guest.full_name}"

class FolioCharge(models.Model):
    """Individual charges on guest folio"""
    CHARGE_TYPES = [
        ('room', 'Room Charge'),
        ('food', 'Food & Beverage'),
        ('laundry', 'Laundry'),
        ('spa', 'Spa Services'),
        ('minibar', 'Minibar'),
        ('phone', 'Phone'),
        ('internet', 'Internet'),
        ('parking', 'Parking'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folio = models.ForeignKey(GuestFolio, on_delete=models.CASCADE, related_name='charges')
    
    charge_type = models.CharField(max_length=20, choices=CHARGE_TYPES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    charged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    charge_date = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.description} - ${self.amount}"

class NightAudit(models.Model):
    """Night audit operations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    audit_date = models.DateField()
    
    # Audit details
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_occupied_rooms = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    arrivals_count = models.PositiveIntegerField(default=0)
    departures_count = models.PositiveIntegerField(default=0)
    no_shows_count = models.PositiveIntegerField(default=0)
    
    # Status
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['property', 'audit_date']
    
    def __str__(self):
        return f"Night Audit - {self.property.name} - {self.audit_date}"