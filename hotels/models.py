from django.db import models
from django.conf import settings
import uuid

class Hotel(models.Model):
    """Hotel model"""
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('AUD', 'Australian Dollar (A$)'),
        ('CAD', 'Canadian Dollar (C$)'),
        ('CHF', 'Swiss Franc (CHF)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('SEK', 'Swedish Krona (kr)'),
        ('NZD', 'New Zealand Dollar (NZ$)'),
        ('MXN', 'Mexican Peso ($)'),
        ('SGD', 'Singapore Dollar (S$)'),
        ('HKD', 'Hong Kong Dollar (HK$)'),
        ('NOK', 'Norwegian Krone (kr)'),
        ('INR', 'Indian Rupee (₹)'),
        ('PKR', 'Pakistani Rupee (₨)'),
        ('BRL', 'Brazilian Real (R$)'),
        ('RUB', 'Russian Ruble (₽)'),
        ('KRW', 'South Korean Won (₩)'),
        ('TRY', 'Turkish Lira (₺)'),
        ('ZAR', 'South African Rand (R)'),
        ('AED', 'UAE Dirham (د.إ)'),
        ('SAR', 'Saudi Riyal (﷼)'),
        ('EGP', 'Egyptian Pound (£)'),
    ]
    
    hotel_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_hotels')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=25, blank=True)
    email = models.EmailField(blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    image = models.ImageField(upload_to='hotel_images/', blank=True, null=True)
    icon = models.ImageField(upload_to='hotel_icons/', blank=True, null=True, help_text='Hotel icon/logo')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True, help_text='Soft delete timestamp')
    is_active = models.BooleanField(default=True)
    
    # Google Drive Configuration
    google_drive_enabled = models.BooleanField(default=False, help_text='Enable Google Drive integration')
    google_drive_folder_id = models.CharField(max_length=200, blank=True, help_text='Google Drive folder ID for storing documents')
    google_service_account_key = models.TextField(blank=True, help_text='Google Service Account JSON key')
    google_drive_share_email = models.EmailField(blank=True, help_text='Email to share uploaded documents with')

    def __str__(self):
        return self.name

class HotelSubscription(models.Model):
    """Hotel subscription model"""
    SUBSCRIPTION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey('tenants.SubscriptionPlan', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES, default='monthly')
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default='active')
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.plan.name}"

class Payment(models.Model):
    """Payment model"""
    PAYMENT_STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.AutoField(primary_key=True)
    hotel_subscription = models.ForeignKey(HotelSubscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50, default='admin_created')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.amount} for {self.hotel_subscription.hotel.name}"

class SubscriptionHistory(models.Model):
    """Subscription history model"""
    ACTION_CHOICES = [
        ('started', 'Started'),
        ('renewed', 'Renewed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    id = models.AutoField(primary_key=True)
    hotel_subscription = models.ForeignKey(HotelSubscription, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    action_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel_subscription.hotel.name} - {self.action}"

class Floor(models.Model):
    """Hotel floor model"""
    id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.IntegerField(help_text='Floor number (e.g., 1, 2, 3, -1 for basement)')
    floor_name = models.CharField(max_length=100, help_text='Floor name (e.g., Ground Floor, Mezzanine, Penthouse)')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['hotel', 'floor_number']
        ordering = ['floor_number']
    
    def __str__(self):
        return f"{self.floor_name} (Floor {self.floor_number}) - {self.hotel.name}"

class Company(models.Model):
    """Company/Corporate client model for hotels"""
    id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=25, blank=True)
    address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True, help_text='Tax ID or Registration Number')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Corporate discount percentage')
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Credit limit for corporate bookings')
    payment_terms = models.CharField(max_length=100, blank=True, help_text='Payment terms (e.g., Net 30 days)')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Companies'
        unique_together = ['hotel', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.hotel.name}"

class RoomCategory(models.Model):
    """Room category model for each hotel"""
    id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_categories')
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    base_price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    amenities = models.TextField(blank=True, help_text='Comma-separated list of amenities')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Room Categories'
        unique_together = ['hotel', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.hotel.name}"

class RoomType(models.Model):
    """Room type model"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    max_occupancy = models.IntegerField(default=2)
    bed_configuration = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class RoomStatus(models.Model):
    """Room status model"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default='#6B7280', help_text='Hex color code')
    is_available_for_booking = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Room Statuses'
    
    def __str__(self):
        return self.name

class Room(models.Model):
    """Enhanced Room model with detailed amenities and features"""
    VIEW_TYPE_CHOICES = [
        ('City', 'City View'),
        ('Garden', 'Garden View'),
        ('Ocean', 'Ocean View'),
        ('Mountain', 'Mountain View'),
        ('Pool', 'Pool View'),
        ('Courtyard', 'Courtyard View'),
    ]
    
    ROOM_STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Occupied', 'Occupied'),
        ('Reserved', 'Reserved'),
        ('Dirty', 'Dirty'),
        ('Cleaning', 'Cleaning'),
        ('Maintenance', 'Maintenance'),
        ('Blocked', 'Blocked'),
    ]
    
    room_id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    floor = models.ForeignKey('configurations.Floor', on_delete=models.SET_NULL, related_name='rooms', null=True, blank=True)
    room_number = models.CharField(max_length=50)
    
    # Basic Details - using configuration models
    room_type = models.ForeignKey('configurations.RoomType', on_delete=models.SET_NULL, related_name='rooms', null=True, blank=True)
    bed_type = models.ForeignKey('configurations.BedType', on_delete=models.SET_NULL, related_name='rooms', null=True, blank=True)
    max_guests = models.PositiveIntegerField(default=2, help_text='Maximum number of guests')
    room_size = models.PositiveIntegerField(default=250, help_text='Room size in square feet')
    view_type = models.CharField(max_length=20, choices=VIEW_TYPE_CHOICES, blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='Available')
    
    # Features & Amenities (Boolean fields for common amenities)
    has_wifi = models.BooleanField(default=True, verbose_name='Free Wi-Fi')
    has_ac = models.BooleanField(default=True, verbose_name='Air Conditioning')
    has_tv = models.BooleanField(default=True, verbose_name='TV')
    has_minibar = models.BooleanField(default=False, verbose_name='Mini Bar')
    has_balcony = models.BooleanField(default=False, verbose_name='Balcony')
    has_work_desk = models.BooleanField(default=False, verbose_name='Work Desk')
    has_seating_area = models.BooleanField(default=False, verbose_name='Seating Area')
    has_kitchenette = models.BooleanField(default=False, verbose_name='Kitchenette')
    has_living_room = models.BooleanField(default=False, verbose_name='Separate Living Room')
    
    # Amenities from configuration
    amenities = models.ManyToManyField('configurations.Amenity', blank=True, related_name='rooms')
    
    # Additional amenities as text field
    additional_amenities = models.TextField(blank=True, help_text='Additional amenities (comma-separated)')
    
    # Room description
    description = models.TextField(blank=True, help_text='Room description')
    
    # Room image
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)
    
    # Services relationship
    services = models.ManyToManyField('Service', blank=True, related_name='rooms')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def amenities_list(self):
        """Get list of all amenities for this room"""
        amenities = []
        
        # Boolean amenities
        if self.has_wifi: amenities.append('Free Wi-Fi')
        if self.has_ac: amenities.append('Air Conditioning')
        if self.has_tv: amenities.append('TV')
        if self.has_minibar: amenities.append('Mini Bar')
        if self.has_balcony: amenities.append('Balcony')
        if self.has_work_desk: amenities.append('Work Desk')
        if self.has_seating_area: amenities.append('Seating Area')
        if self.has_kitchenette: amenities.append('Kitchenette')
        if self.has_living_room: amenities.append('Separate Living Room')
        
        # Configuration amenities
        for amenity in self.amenities.all():
            amenities.append(amenity.name)
        
        # Add additional amenities
        if self.additional_amenities:
            additional = [a.strip() for a in self.additional_amenities.split(',') if a.strip()]
            amenities.extend(additional)
            
        return amenities
    

    
    class Meta:
        unique_together = ['hotel', 'room_number']
    
    def __str__(self):
        floor_info = f" on {self.floor.name}" if self.floor else ""
        category_info = f" ({self.category.name})" if self.category else ""
        room_type_info = f" {self.room_type.name}" if self.room_type else ""
        return f"Room {self.room_number}{room_type_info}{category_info}{floor_info} - {self.hotel.name}"
    
    @property
    def display_name(self):
        """Display name for room directory"""
        parts = [f"Room {self.room_number}"]
        if self.room_type:
            parts.append(f"{self.room_type.name}")
        if self.category:
            parts.append(f"({self.category.name})")
        if self.floor:
            parts.append(f"on {self.floor.name}")
        return " ".join(parts)

class Service(models.Model):
    """Hotel services model"""
    service_id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.hotel.name}"