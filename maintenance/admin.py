from django.contrib import admin
from django.utils.html import format_html
from .models import MaintenanceIssue

@admin.register(MaintenanceIssue)
class MaintenanceIssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'priority', 'status', 'reported_at']
    list_filter = ['category', 'priority', 'status', 'reported_at']
    search_fields = ['title', 'description']
    
