from django.db import models
from reservations.models import Stay
from crm.models import GuestProfile
import uuid
from decimal import Decimal

class TaxConfiguration(models.Model):
    """Tax configuration for hotels"""
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.percentage}%"
    
    class Meta:
        ordering = ['name']

class Invoice(models.Model):
    """Invoice model for guest billing"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stay = models.OneToOneField(Stay, on_delete=models.CASCADE, related_name='invoice')
    guest = models.ForeignKey(GuestProfile, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_date = models.DateField(null=True, blank=True)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    currency = models.CharField(max_length=10, default='USD')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"
    
    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount
    
    def calculate_totals(self):
        """Calculate invoice totals from charge items"""
        charge_items = self.charge_items.all()
        self.subtotal = sum(item.amount for item in charge_items)
        
        # Calculate tax amount based on tax rate
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = taxable_amount * (self.tax_rate / 100)
        
        # Service charge is 5% default
        self.service_charge = taxable_amount * Decimal('0.05')
        
        self.total_amount = self.subtotal + self.tax_amount + self.service_charge - self.discount_amount
        self.save()

class ChargeItem(models.Model):
    """Individual charge items on an invoice"""
    CHARGE_TYPE_CHOICES = [
        ('room', 'Room Charge'),
        ('food', 'Food & Beverage'),
        ('laundry', 'Laundry'),
        ('spa', 'Spa Services'),
        ('minibar', 'Minibar'),
        ('phone', 'Phone Charges'),
        ('internet', 'Internet'),
        ('parking', 'Parking'),
        ('service', 'Service Charge'),
        ('tax', 'Tax'),
        ('deposit', 'Deposit'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='charge_items')
    description = models.CharField(max_length=255)
    charge_type = models.CharField(max_length=20, choices=CHARGE_TYPE_CHOICES, default='other')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.description} - {self.amount}"

class Payment(models.Model):
    """Payment records for invoices"""
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('check', 'Check'),
        ('mobile_payment', 'Mobile Payment'),
        ('crypto', 'Cryptocurrency'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_number = models.CharField(max_length=100, blank=True)
    gateway_transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.amount}"

class Deposit(models.Model):
    """Security deposits for reservations"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('collected', 'Collected'),
        ('refunded', 'Refunded'),
        ('forfeited', 'Forfeited'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stay = models.OneToOneField(Stay, on_delete=models.CASCADE, related_name='deposit')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    collected_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Deposit {self.amount} - {self.stay.reservation.guest.full_name}"