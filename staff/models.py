from django.db import models
from django.contrib.auth.models import Group, Permission
from accounts.models import User
import uuid

class Role(models.Model):
    """Custom role model for RBAC"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class Staff(models.Model):
    """Staff model for property-level employees"""
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('receptionist', 'Receptionist'),
        ('housekeeper', 'Housekeeper'),
        ('maintenance', 'Maintenance'),
        ('security', 'Security'),
        ('concierge', 'Concierge'),
        ('chef', 'Chef'),
        ('admin', 'Admin'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    hire_date = models.DateField()
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    department = models.CharField(max_length=50, blank=True)
    shift_start = models.TimeField(null=True, blank=True)
    shift_end = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role} at {self.property.name}"
    
    def get_permissions(self):
        """Get all permissions for this staff member"""
        permissions = set()
        if self.custom_role:
            permissions.update(self.custom_role.permissions.all())
        return permissions

class StaffSchedule(models.Model):
    """Staff scheduling model"""
    SHIFT_TYPE_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('night', 'Night'),
        ('full_day', 'Full Day'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    shift_type = models.CharField(max_length=20, choices=SHIFT_TYPE_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_off_day = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['staff', 'date']
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.date} ({self.shift_type})"