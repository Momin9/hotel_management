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
    address = models.CharField(max_length=5000, blank=True)
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
    BUSINESS_TYPE_CHOICES = [
        ('it_software', 'IT / Software'),
        ('banking_finance', 'Banking & Finance'),
        ('government_public', 'Government / Public Sector'),
        ('education', 'Education'),
        ('healthcare', 'Healthcare'),
        ('manufacturing_industrial', 'Manufacturing & Industrial'),
        ('construction_realestate', 'Construction / Real Estate'),
        ('consulting_services', 'Consulting / Services'),
        ('logistics_transportation', 'Logistics & Transportation'),
        ('retail_fmcg', 'Retail / FMCG'),
        ('hospitality_tourism', 'Hospitality / Tourism'),
        ('ngo_nonprofit', 'NGO / Non-Profit'),
        ('other', 'Other'),
    ]
    
    BILLING_MODE_CHOICES = [
        ('company_pays', 'Company Pays'),
        ('guest_pays', 'Guest Pays'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blacklisted', 'Blacklisted'),
    ]
    
    id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='companies')
    
    # Company Information
    name = models.CharField(max_length=200, help_text='Company Name')
    business_type = models.CharField(max_length=30, choices=BUSINESS_TYPE_CHOICES, default='it_software')
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, help_text='Company Logo (optional)')
    registration_number = models.CharField(max_length=100, blank=True, help_text='Registration/Tax Number (optional)')
    
    # Contact Information
    address = models.TextField(blank=True, help_text='Registered Address')
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=25, blank=True, help_text='Phone Number')
    email = models.EmailField(blank=True, help_text='Company Email')
    website = models.URLField(blank=True, help_text='Website (optional)')
    
    # Authorized Person
    contact_person = models.CharField(max_length=100, blank=True, help_text='Contact Person Name')
    designation = models.CharField(max_length=100, blank=True, help_text='Designation')
    mobile_number = models.CharField(max_length=25, blank=True, help_text='Mobile Number')
    contact_email = models.EmailField(blank=True, help_text='Contact Person Email')
    
    # Contract Details
    contract_start_date = models.DateField(null=True, blank=True, help_text='Contract Start Date')
    contract_end_date = models.DateField(null=True, blank=True, help_text='Contract End Date')
    approved_room_types = models.ManyToManyField('configurations.RoomType', blank=True, related_name='approved_companies', help_text='Approved Room Types')
    corporate_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Corporate Discount (%)')
    billing_mode = models.CharField(max_length=20, choices=BILLING_MODE_CHOICES, default='company_pays')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    
    # Legacy fields (keeping for backward compatibility)
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
    
    @property
    def is_contract_active(self):
        """Check if contract is currently active based on dates"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.contract_start_date <= today <= self.contract_end_date


class CompanyRoomRate(models.Model):
    """Fixed corporate rates for specific room types"""
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='room_rates')
    room_type = models.ForeignKey('configurations.RoomType', on_delete=models.CASCADE)
    rate_per_night = models.DecimalField(max_digits=12, decimal_places=2, help_text='Fixed rate per night')
    currency = models.CharField(max_length=3, default='PKR')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['company', 'room_type']
        verbose_name = 'Company Room Rate'
        verbose_name_plural = 'Company Room Rates'
    
    def __str__(self):
        return f"{self.company.name} - {self.room_type.name}: {self.currency} {self.rate_per_night}/night"

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
    hotels = models.ManyToManyField(Hotel, related_name='services')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.hotel.name}"