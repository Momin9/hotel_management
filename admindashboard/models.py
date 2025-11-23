from django.db import models


class VisitorStats(models.Model):
    visitors = models.IntegerField()
    growth_percentage = models.FloatField()
    last_month = models.FloatField()


class BookingStats(models.Model):
    bookings = models.IntegerField()
    growth_percentage = models.FloatField()
    last_month = models.FloatField()


class RevenueStats(models.Model):
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    growth_percentage = models.FloatField()
    last_month = models.FloatField()


class RoomStats(models.Model):
    available_rooms = models.IntegerField()
    total_rooms = models.IntegerField()
    growth_percentage = models.FloatField()
    last_month = models.FloatField()


class Booking(models.Model):
    guest_name = models.CharField(max_length=255)
    check_in = models.DateField()
    check_out = models.DateField()
    proof = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50)
    number_of_members = models.IntegerField()
    number_of_rooms = models.IntegerField()


class TeamMember(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
