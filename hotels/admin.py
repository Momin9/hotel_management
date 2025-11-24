from django.contrib import admin
from django.utils.html import format_html
from .models import Hotel, HotelSubscription, Room, Service, RoomCategory, RoomType, RoomStatus

class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    max_num = 20
    fields = ['room_number', 'type', 'category', 'bed', 'price', 'status']

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    max_num = 10
    fields = ['name', 'description', 'price']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['icon_preview', 'name', 'owner', 'city', 'country', 'room_count', 'is_active_badge', 'created_at']
    list_filter = ['is_active', 'city', 'country', 'created_at']
    search_fields = ['name', 'address', 'phone', 'email', 'owner__username']
    readonly_fields = ['hotel_id', 'created_at']
    inlines = [RoomInline, ServiceInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'owner', 'address', 'city', 'country')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Media', {
            'fields': ('image', 'icon')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('hotel_id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def room_count(self, obj):
        count = obj.rooms.count()
        return f"{count} rooms"
    room_count.short_description = 'Total Rooms'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_badge.short_description = 'Status'
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 4px;" />', obj.icon.url)
        return format_html('<div style="width: 30px; height: 30px; background: #f3f4f6; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #6b7280;">🏨</div>')
    icon_preview.short_description = 'Icon'

@admin.register(HotelSubscription)
class HotelSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'plan', 'start_date', 'end_date', 'status', 'auto_renew']
    list_filter = ['status', 'auto_renew', 'start_date', 'end_date']
    search_fields = ['hotel__name', 'plan__name']
    readonly_fields = ['created_at']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'hotel', 'type', 'category', 'price', 'status']
    list_filter = ['status', 'type', 'category', 'bed', 'hotel']
    search_fields = ['room_number', 'hotel__name']
    list_editable = ['status', 'price']
    
    def status_badge(self, obj):
        colors = {
            'Available': '#10B981',
            'Occupied': '#F59E0B',
            'Reserved': '#3B82F6',
            'Dirty': '#8B5CF6',
            'Cleaning': '#06B6D4',
            'Maintenance': '#EF4444',
            'Blocked': '#6B7280'
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'
    
    actions = ['mark_available', 'mark_dirty', 'mark_maintenance']
    
    def mark_available(self, request, queryset):
        queryset.update(status='Available')
        self.message_user(request, f'{queryset.count()} rooms marked as available.')
    mark_available.short_description = 'Mark as Available'
    
    def mark_dirty(self, request, queryset):
        queryset.update(status='Dirty')
        self.message_user(request, f'{queryset.count()} rooms marked as dirty.')
    mark_dirty.short_description = 'Mark as Dirty'
    
    def mark_maintenance(self, request, queryset):
        queryset.update(status='Maintenance')
        self.message_user(request, f'{queryset.count()} rooms marked for maintenance.')
    mark_maintenance.short_description = 'Mark for Maintenance'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'hotel', 'price', 'created_at']
    list_filter = ['hotel', 'created_at']
    search_fields = ['name', 'description', 'hotel__name']

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price_multiplier', 'created_at']
    search_fields = ['name', 'description']

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_occupancy', 'bed_configuration', 'created_at']
    search_fields = ['name', 'description']

@admin.register(RoomStatus)
class RoomStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_code', 'is_available_for_booking', 'created_at']
    list_filter = ['is_available_for_booking']
    search_fields = ['name', 'description']