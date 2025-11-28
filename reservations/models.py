from django.db import models
from django.utils import timezone
from crm.models import GuestProfile
import uuid

class Reservation(models.Model):
    """Reservation model for booking management"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    BOOKING_SOURCE_CHOICES = [
        ('direct', 'Direct'),
        ('online', 'Online'),
        ('phone', 'Phone'),
        ('walk_in', 'Walk-in'),
        ('ota', 'OTA'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest = models.ForeignKey(GuestProfile, on_delete=models.CASCADE, related_name='reservations')
    hotel = models.ForeignKey('hotels.Hotel', on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey('hotels.Room', on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_source = models.CharField(max_length=20, choices=BOOKING_SOURCE_CHOICES, default='direct')
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Reservation {self.id} - {self.guest.full_name}"
    
    @property
    def total_nights(self):
        return (self.check_out - self.check_in).days
    
    @property
    def total_amount(self):
        return self.rate * self.total_nights

class Stay(models.Model):
    """Actual stay record when guest checks in"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='stay')
    room = models.ForeignKey('hotels.Room', on_delete=models.CASCADE, related_name='stays')
    actual_check_in = models.DateTimeField()
    actual_check_out = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Stay {self.id} - Room {self.room.room_number}"

class ReservationExpense(models.Model):
    """Additional expenses during guest stay"""
    EXPENSE_TYPE_CHOICES = [
        ('food', 'Food & Beverage'),
        ('laundry', 'Laundry Service'),
        ('spa', 'Spa Services'),
        ('minibar', 'Minibar'),
        ('phone', 'Phone Charges'),
        ('internet', 'Internet'),
        ('parking', 'Parking'),
        ('transport', 'Transportation'),
        ('room_service', 'Room Service'),
        ('extra_bed', 'Extra Bed'),
        ('late_checkout', 'Late Checkout'),
        ('damage', 'Damage Charges'),
        ('other', 'Other Services'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPE_CHOICES, default='other')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    added_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.description} - ${self.total_amount}"
    
    class Meta:
        ordering = ['-date_added']