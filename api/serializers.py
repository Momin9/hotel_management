from rest_framework import serializers
from hotels.models import Hotel, Room
from reservations.models import Reservation, Stay
from crm.models import GuestProfile
from front_desk.models import CheckInOut, GuestFolio
from housekeeping.models import HousekeepingTask
from maintenance.models import MaintenanceIssue
from pos.models import POSOrder, POSItem
from inventory.models import InventoryItem, StockMovement

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    
    class Meta:
        model = Room
        fields = '__all__'

class GuestProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestProfile
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    
    class Meta:
        model = Reservation
        fields = '__all__'

class CheckInOutSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    
    class Meta:
        model = CheckInOut
        fields = '__all__'

class GuestFolioSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    
    class Meta:
        model = GuestFolio
        fields = '__all__'

class HousekeepingTaskSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    staff_name = serializers.CharField(source='assigned_staff.user.get_full_name', read_only=True)
    
    class Meta:
        model = HousekeepingTask
        fields = '__all__'

class MaintenanceIssueSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.user.get_full_name', read_only=True)
    
    class Meta:
        model = MaintenanceIssue
        fields = '__all__'

class POSItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = POSItem
        fields = '__all__'

class POSOrderSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = POSOrder
        fields = '__all__'

class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='primary_supplier.name', read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = '__all__'

class StockMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = '__all__'

# Dashboard serializers
class DashboardStatsSerializer(serializers.Serializer):
    total_rooms = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    available_rooms = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_maintenance = serializers.IntegerField()
    housekeeping_tasks = serializers.IntegerField()
    
class OccupancyDataSerializer(serializers.Serializer):
    date = serializers.DateField()
    occupancy_rate = serializers.FloatField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)

class RevenueDataSerializer(serializers.Serializer):
    month = serializers.CharField()
    room_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    pos_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)