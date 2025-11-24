from django.contrib import admin
from django.utils.html import format_html
from .models import Staff, Role, StaffSchedule

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    search_fields = ['name', 'description']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'employee_id', 'department', 'employment_status', 'hire_date']
    list_filter = ['department', 'employment_status', 'hire_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id']
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = 'Name'

@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ['staff_name', 'date', 'shift_type', 'start_time', 'end_time']
    list_filter = ['date', 'shift_type']
    search_fields = ['staff__user__username', 'staff__user__first_name', 'staff__user__last_name']
    
    def staff_name(self, obj):
        return obj.staff.user.get_full_name() or obj.staff.user.username
    staff_name.short_description = 'Staff Member'