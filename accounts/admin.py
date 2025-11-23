from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, AboutUs

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('created_at',)
    filter_horizontal = ('groups', 'user_permissions')

@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'updated_at')
    fieldsets = (
        ('Mission & Purpose', {
            'fields': ('mission_statement', 'problem_description', 'solution_description', 'problem_icon', 'solution_icon', 'mission_icon')
        }),
        ('Trust & Reliability', {
            'fields': ('global_architecture_text', 'data_security_text', 'modern_tech_text')
        }),
        ('Trust Indicators', {
            'fields': ('uptime_percentage', 'security_monitoring', 'security_certification', 'compliance_standard')
        }),
        ('Contact Information', {
            'fields': ('support_email', 'support_phone', 'support_hours')
        }),
        ('Settings', {
            'fields': ('is_active',)
        })
    )
    
    def has_add_permission(self, request):
        # Only allow one AboutUs instance
        return not AboutUs.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False

# Unregister the default Group admin_dashboard to prevent conflicts
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
