from django.db import models
import uuid

class RoomType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotels = models.ManyToManyField('hotels.Hotel', related_name='config_room_types')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class RoomCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotels = models.ManyToManyField('hotels.Hotel', related_name='config_room_categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_occupancy = models.IntegerField(default=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Room Categories"

class BedType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotels = models.ManyToManyField('hotels.Hotel', related_name='config_bed_types')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    usage = models.CharField(max_length=100, blank=True, help_text="How this bed type is typically used (e.g., Single occupancy, Double occupancy, Kids bed)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Floor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotels = models.ManyToManyField('hotels.Hotel', related_name='config_floors')
    name = models.CharField(max_length=100)
    number = models.IntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Floor {self.number} - {self.name}"
    
    class Meta:
        ordering = ['number']

class Amenity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotels = models.ManyToManyField('hotels.Hotel', related_name='config_amenities')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Amenities"