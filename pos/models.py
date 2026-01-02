from django.db import models
from django.conf import settings

from crm.models import GuestProfile
# from front_desk.models import GuestFolio
import uuid

class POSCategory(models.Model):
    """POS item categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class POSItem(models.Model):
    """POS menu items"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(POSCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Inventory tracking
    track_inventory = models.BooleanField(default=False)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    
    # Status
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    @property
    def is_low_stock(self):
        return self.track_inventory and self.stock_quantity <= self.low_stock_threshold

class POSOrder(models.Model):
    """POS orders"""
    ORDER_TYPES = [
        ('dine_in', 'Dine In'),
        ('room_service', 'Room Service'),
        ('takeaway', 'Takeaway'),
        ('delivery', 'Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('charged_to_room', 'Charged to Room'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES, default='dine_in')
    
    # Customer details
    guest = models.ForeignKey(GuestProfile, on_delete=models.SET_NULL, null=True, blank=True)
    # guest_folio = models.ForeignKey(GuestFolio, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    room_number = models.CharField(max_length=20, blank=True)
    table_number = models.CharField(max_length=20, blank=True)
    
    # Order details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    
    # Staff
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pos_orders_created')
    served_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pos_orders_served')
    
    # Timestamps
    order_time = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)
    
    # Special instructions
    special_instructions = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Order {self.order_number} - ${self.total_amount}"
    
    def calculate_totals(self):
        """Calculate order totals"""
        from decimal import Decimal
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.tax_amount = self.subtotal * Decimal('0.10')  # 10% tax
        self.service_charge = self.subtotal * Decimal('0.05')  # 5% service charge
        self.total_amount = self.subtotal + self.tax_amount + self.service_charge - self.discount_amount
        self.save()

class POSOrderItem(models.Model):
    """Individual items in POS orders"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(POSOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(POSItem, on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Customizations
    special_instructions = models.TextField(blank=True)
    modifications = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity}x {self.item.name}"

class POSPayment(models.Model):
    """POS payment records"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('room_charge', 'Room Charge'),
        ('digital_wallet', 'Digital Wallet'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(POSOrder, on_delete=models.CASCADE, related_name='payments')
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment details
    reference_number = models.CharField(max_length=100, blank=True)
    card_last_four = models.CharField(max_length=4, blank=True)
    
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    processed_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment {self.payment_method} - ${self.amount}"

class POSShift(models.Model):
    """POS shift management"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey('hotels.Hotel', on_delete=models.CASCADE)
    staff_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    shift_date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Cash handling
    opening_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    closing_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    card_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Shift summary
    orders_count = models.PositiveIntegerField(default=0)
    is_closed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Shift {self.staff_member.username} - {self.shift_date}"

class MiniBartItem(models.Model):
    """Minibar items tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(POSItem, on_delete=models.CASCADE)
    room = models.ForeignKey('hotels.Room', on_delete=models.CASCADE)
    
    quantity_stocked = models.PositiveIntegerField(default=0)
    quantity_consumed = models.PositiveIntegerField(default=0)
    last_restocked = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.item.name} - Room {self.room.room_number}"