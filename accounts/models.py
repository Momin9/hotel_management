import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError


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
    copyright_text = models.CharField(max_length=200, default="© 2024 AuraStay Management Suite. All rights reserved.")
    
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