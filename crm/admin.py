from django.contrib import admin
from django.utils.html import format_html
from .models import GuestProfile

@admin.register(GuestProfile)
class GuestProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'nationality', 'loyalty_status_badge', 'loyalty_points', 'created_at']
    list_filter = ['loyalty_status', 'nationality', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'nationality')
        }),
        ('Address & Notes', {
            'fields': ('address', 'notes', 'preferences')
        }),
        ('Loyalty Program', {
            'fields': ('loyalty_status', 'loyalty_points')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def loyalty_status_badge(self, obj):
        colors = {
            'bronze': '#CD7F32',
            'silver': '#C0C0C0', 
            'gold': '#FFD700',
            'platinum': '#E5E4E2'
        }
        color = colors.get(obj.loyalty_status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_loyalty_status_display()
        )
    loyalty_status_badge.short_description = 'Loyalty Status'
    
    actions = ['upgrade_to_silver', 'upgrade_to_gold', 'reset_loyalty_points']
    
    def upgrade_to_silver(self, request, queryset):
        queryset.update(loyalty_status='silver')
        self.message_user(request, f'{queryset.count()} guests upgraded to Silver status.')
    upgrade_to_silver.short_description = 'Upgrade selected guests to Silver'
    
    def upgrade_to_gold(self, request, queryset):
        queryset.update(loyalty_status='gold')
        self.message_user(request, f'{queryset.count()} guests upgraded to Gold status.')
    upgrade_to_gold.short_description = 'Upgrade selected guests to Gold'
    
    def reset_loyalty_points(self, request, queryset):
        queryset.update(loyalty_points=0)
        self.message_user(request, f'Loyalty points reset for {queryset.count()} guests.')
    reset_loyalty_points.short_description = 'Reset loyalty points'