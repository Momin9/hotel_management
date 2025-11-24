import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Hotel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hotel')
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.owner.is_hotel_owner:
            raise ValidationError("The selected user is not a hotel owner.")

    def __str__(self):
        return self.name


class Guest(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='guests')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    government_id = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(max_length=200)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    additional_guests = models.TextField(max_length=200)
    gender = models.CharField(
        max_length=6,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        default='Male'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"


class Employee(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    hotel = models.ForeignKey('hotel.Hotel', on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    role = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.role}"
