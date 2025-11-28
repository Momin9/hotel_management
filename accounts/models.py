import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Owner', 'Owner'),
        ('Manager', 'Manager'),
        ('Staff', 'Staff'),
    ]
    
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Staff')
    assigned_hotel = models.ForeignKey('hotels.Hotel', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members')
    temp_password = models.CharField(max_length=128, blank=True, null=True, help_text='Temporary storage for password to send in emails')
    deleted_at = models.DateTimeField(null=True, blank=True, help_text='Soft delete timestamp')
    
    # Hotel Management Permissions
    can_view_hotels = models.BooleanField(default=False, help_text='Can view hotel information')
    can_change_hotels = models.BooleanField(default=False, help_text='Can edit hotel settings')
    can_view_rooms = models.BooleanField(default=False, help_text='Can view rooms')
    can_add_rooms = models.BooleanField(default=False, help_text='Can add new rooms')
    can_change_rooms = models.BooleanField(default=False, help_text='Can edit room details')
    can_delete_rooms = models.BooleanField(default=False, help_text='Can delete rooms')
    
    # Reservations Permissions
    can_view_reservations = models.BooleanField(default=False, help_text='Can view reservations')
    can_add_reservations = models.BooleanField(default=False, help_text='Can create reservations')
    can_change_reservations = models.BooleanField(default=False, help_text='Can edit reservations')
    can_delete_reservations = models.BooleanField(default=False, help_text='Can cancel reservations')
    can_view_checkins = models.BooleanField(default=False, help_text='Can view check-ins')
    can_add_checkins = models.BooleanField(default=False, help_text='Can process check-ins')
    can_change_checkins = models.BooleanField(default=False, help_text='Can modify check-ins')
    
    # Guest Management Permissions
    can_view_guests = models.BooleanField(default=False, help_text='Can view guest profiles')
    can_add_guests = models.BooleanField(default=False, help_text='Can add new guests')
    can_change_guests = models.BooleanField(default=False, help_text='Can edit guest information')
    can_delete_guests = models.BooleanField(default=False, help_text='Can delete guest profiles')
    
    # Staff Management Permissions
    can_view_staff = models.BooleanField(default=False, help_text='Can view staff list')
    can_add_staff = models.BooleanField(default=False, help_text='Can add new staff')
    can_change_staff = models.BooleanField(default=False, help_text='Can edit staff details')
    can_delete_staff = models.BooleanField(default=False, help_text='Can remove staff')
    
    # Housekeeping Permissions
    can_view_housekeeping = models.BooleanField(default=False, help_text='Can view housekeeping tasks')
    can_add_housekeeping = models.BooleanField(default=False, help_text='Can create housekeeping tasks')
    can_change_housekeeping = models.BooleanField(default=False, help_text='Can update task status')
    can_delete_housekeeping = models.BooleanField(default=False, help_text='Can delete tasks')
    
    # Maintenance Permissions
    can_view_maintenance = models.BooleanField(default=False, help_text='Can view maintenance issues')
    can_add_maintenance = models.BooleanField(default=False, help_text='Can report new issues')
    can_change_maintenance = models.BooleanField(default=False, help_text='Can update issue status')
    can_delete_maintenance = models.BooleanField(default=False, help_text='Can close issues')
    
    # Point of Sale Permissions
    can_view_pos = models.BooleanField(default=False, help_text='Can view POS orders')
    can_add_pos = models.BooleanField(default=False, help_text='Can create orders')
    can_change_pos = models.BooleanField(default=False, help_text='Can modify orders')
    can_delete_pos = models.BooleanField(default=False, help_text='Can cancel orders')
    
    # Inventory Permissions
    can_view_inventory = models.BooleanField(default=False, help_text='Can view inventory')
    can_add_inventory = models.BooleanField(default=False, help_text='Can add inventory items')
    can_change_inventory = models.BooleanField(default=False, help_text='Can update inventory')
    can_delete_inventory = models.BooleanField(default=False, help_text='Can remove items')
    
    # Financial Permissions
    can_view_billing = models.BooleanField(default=False, help_text='Can view billing information')
    can_add_billing = models.BooleanField(default=False, help_text='Can create invoices')
    can_change_billing = models.BooleanField(default=False, help_text='Can edit billing')
    can_view_payments = models.BooleanField(default=False, help_text='Can view payments')
    can_add_payments = models.BooleanField(default=False, help_text='Can process payments')
    can_view_reports = models.BooleanField(default=False, help_text='Can view financial reports')
    
    # Configuration Permissions
    can_view_configurations = models.BooleanField(default=False, help_text='Can view configuration lists')
    can_add_configurations = models.BooleanField(default=False, help_text='Can create new configurations')
    can_change_configurations = models.BooleanField(default=False, help_text='Can edit existing configurations')
    can_delete_configurations = models.BooleanField(default=False, help_text='Can delete configurations')
    
    # Company Management Permissions
    can_view_companies = models.BooleanField(default=False, help_text='Can view company contracts')
    can_add_companies = models.BooleanField(default=False, help_text='Can create company contracts')
    can_change_companies = models.BooleanField(default=False, help_text='Can edit company contracts')
    can_delete_companies = models.BooleanField(default=False, help_text='Can delete company contracts')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_users',  # Change related_name to avoid conflict
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_users',  # Change related_name to avoid conflict
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_role(self):
        return self.get_role_display()
    
    def get_full_name(self):
        return self.full_name
    
    def get_short_name(self):
        return self.first_name


class AboutUs(models.Model):
    """About Us page content model"""
    # Purpose Section
    purpose_title = models.CharField(max_length=200, default="Our Purpose: Why AuraStay Exists", help_text='Title for the purpose section')
    purpose_icon = models.CharField(max_length=50, default='fas fa-rocket', help_text='FontAwesome icon class for purpose section')
    
    # Trust & Reliability Section
    trust_title = models.CharField(max_length=200, default="Trust & Reliability", help_text='Title for the trust section')
    trust_subtitle = models.CharField(max_length=200, default="Built for the modern hospitality industry", help_text='Subtitle for the trust section')
    trust_icon = models.CharField(max_length=50, default='fas fa-shield-alt', help_text='FontAwesome icon class for trust section')
    
    mission_statement = models.TextField(help_text='Main mission statement')
    mission_description = models.TextField(help_text='Description of our mission', blank=True)
    problem_description = models.TextField(help_text='Description of the problem we solve')
    solution_description = models.TextField(help_text='Description of our solution')
    
    # Icons for sections
    problem_icon = models.CharField(max_length=50, default='fas fa-exclamation-triangle', help_text='FontAwesome icon class for problem section')
    solution_icon = models.CharField(max_length=50, default='fas fa-lightbulb', help_text='FontAwesome icon class for solution section')
    mission_icon = models.CharField(max_length=50, default='fas fa-target', help_text='FontAwesome icon class for mission section')
    
    # Trust & Reliability
    global_architecture_text = models.TextField(help_text='Global architecture description')
    data_security_text = models.TextField(help_text='Data security description')
    modern_tech_text = models.TextField(help_text='Modern technology description')
    
    # Trust indicators
    uptime_percentage = models.CharField(max_length=10, default='99.9%')
    security_monitoring = models.CharField(max_length=20, default='24/7')
    security_certification = models.CharField(max_length=20, default='ISO 27001')
    compliance_standard = models.CharField(max_length=20, default='GDPR')
    
    # Contact information
    support_email = models.EmailField(default='support@aurastay.com')
    support_phone = models.CharField(max_length=20, default='+1 (555) 123-4567')
    support_hours = models.CharField(max_length=20, default='24/7 Support')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'About Us'
        verbose_name_plural = 'About Us'
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and AboutUs.objects.exists():
            raise ValidationError('Only one About Us page can exist.')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'About Us Content (Updated: {self.updated_at.strftime("%Y-%m-%d")})'


class Footer(models.Model):
    # Company Info
    company_name = models.CharField(max_length=100, default="AuraStay")
    company_logo = models.ImageField(upload_to='logos/', blank=True, null=True, help_text='Upload company logo (recommended: 200x200px)')
    company_description = models.TextField(default="The world's most advanced hotel management platform, designed for luxury hospitality.")
    
    # Contact Information
    email = models.EmailField(default="info@aurastay.com")
    phone = models.CharField(max_length=20, default="+1 (555) 123-4567")
    address_line1 = models.CharField(max_length=100, default="123 Business Ave")
    address_line2 = models.CharField(max_length=100, default="New York, NY 10001")
    
    # Social Media Links
    twitter_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    
    # Copyright
    copyright_line1 = models.CharField(max_length=200, default="© 2025 AuraStay. All rights reserved.")
    copyright_line2 = models.CharField(max_length=200, default="Design: MA Qureshi | Development: Momin Ali")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Footer Content"
        verbose_name_plural = "Footer Content"
    
    def __str__(self):
        return f"Footer - {self.company_name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and Footer.objects.exists():
            raise ValidationError('Only one Footer configuration can exist.')
        super().save(*args, **kwargs)


class PageContent(models.Model):
    page_name = models.CharField(max_length=50, unique=True, help_text="Unique identifier for the page (e.g., 'profile', 'subscription_plans_create')")
    page_title = models.CharField(max_length=200, help_text="Main page title")
    page_subtitle = models.TextField(help_text="Page subtitle/description")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Page Content"
        verbose_name_plural = "Page Contents"
    
    def __str__(self):
        return f"{self.page_name} - {self.page_title}"


class PasswordResetOTP(models.Model):
    """OTP for password reset"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp}"


class Feature(models.Model):
    """Features section for landing page"""
    
    ICON_CHOICES = [
        ('fas fa-calendar-check', 'Calendar Check'),
        ('fas fa-users', 'Users'),
        ('fas fa-chart-line', 'Chart Line'),
        ('fas fa-broom', 'Broom'),
        ('fas fa-credit-card', 'Credit Card'),
        ('fas fa-mobile-alt', 'Mobile'),
        ('fas fa-shield-alt', 'Shield'),
        ('fas fa-cog', 'Settings'),
        ('fas fa-bell', 'Bell'),
        ('fas fa-database', 'Database'),
    ]
    
    COLOR_CHOICES = [
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('purple', 'Purple'),
        ('red', 'Red'),
        ('yellow', 'Yellow'),
        ('indigo', 'Indigo'),
        ('pink', 'Pink'),
        ('gray', 'Gray'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='fas fa-cog')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='blue')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Feature'
        verbose_name_plural = 'Features'
    
    def __str__(self):
        return self.title


class SiteConfiguration(models.Model):
    """Global site configuration - single instance for entire platform"""
    
    # Company Branding
    company_name = models.CharField(max_length=100, default="AuraStay")
    company_logo = models.ImageField(
        upload_to='site_logos/', 
        blank=True, 
        null=True, 
        help_text='Main company logo used throughout the site (navbar, footer, login, etc.)'
    )
    
    # Site Settings
    site_title = models.CharField(max_length=200, default="AuraStay - Hotel Management System")
    site_description = models.TextField(default="The world's most advanced hotel management platform")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValidationError('Only one Site Configuration can exist.')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Site Config - {self.company_name}"
    
    @classmethod
    def get_instance(cls):
        """Get or create the single site configuration instance"""
        instance, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'company_name': 'AuraStay',
                'site_title': 'AuraStay - Hotel Management System',
                'site_description': "The world's most advanced hotel management platform"
            }
        )
        return instance


class ContactInquiry(models.Model):
    """Contact form submissions from landing page"""
    
    ROOM_COUNT_CHOICES = [
        ('1-50', '1-50 rooms'),
        ('51-150', '51-150 rooms'),
        ('151-300', '151-300 rooms'),
        ('300+', '300+ rooms'),
    ]
    
    SUBJECT_CHOICES = [
        ('demo', 'Request a Demo'),
        ('general', 'General Inquiry'),
        ('support', 'Support'),
        ('pricing', 'Pricing Information'),
        ('partnership', 'Partnership Opportunity'),
    ]
    
    HEAR_ABOUT_CHOICES = [
        ('google', 'Google Search'),
        ('social_media', 'Social Media'),
        ('referral', 'Referral'),
        ('advertisement', 'Advertisement'),
        ('conference', 'Conference/Event'),
        ('other', 'Other'),
    ]
    
    # Essential Contact
    full_name = models.CharField(max_length=100)
    work_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    
    # Business Context
    hotel_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=100)
    number_of_rooms = models.CharField(max_length=20, choices=ROOM_COUNT_CHOICES)
    
    # Inquiry Details
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    
    # Optional
    hear_about_us = models.CharField(max_length=50, choices=HEAR_ABOUT_CHOICES, blank=True)
    privacy_consent = models.BooleanField(default=False)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.hotel_name} ({self.get_subject_display()})"


class TermsOfService(models.Model):
    """Terms of Service content with rich text editor"""
    title = models.CharField(max_length=200, default="Terms of Service")
    content = CKEditor5Field('Content', config_name='terms_privacy', help_text="Terms of Service content with rich text formatting")
    effective_date = models.DateField(help_text="Date when these terms become effective")
    version = models.CharField(max_length=20, default="1.0", help_text="Version number")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Terms of Service"
        verbose_name_plural = "Terms of Service"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate all other active terms
            TermsOfService.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} v{self.version} ({'Active' if self.is_active else 'Inactive'})"


class PrivacyPolicy(models.Model):
    """Privacy Policy content with rich text editor"""
    title = models.CharField(max_length=200, default="Privacy Policy")
    content = CKEditor5Field('Content', config_name='terms_privacy', help_text="Privacy Policy content with rich text formatting")
    effective_date = models.DateField(help_text="Date when this policy becomes effective")
    version = models.CharField(max_length=20, default="1.0", help_text="Version number")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Privacy Policy"
        verbose_name_plural = "Privacy Policy"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate all other active policies
            PrivacyPolicy.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} v{self.version} ({'Active' if self.is_active else 'Inactive'})"