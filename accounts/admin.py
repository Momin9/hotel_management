from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, AboutUs, Footer, PageContent, ContactInquiry

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
            'fields': ('mission_statement', 'mission_description', 'problem_description', 'solution_description', 'problem_icon', 'solution_icon', 'mission_icon')
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

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'company_description')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'address_line1', 'address_line2')
        }),
        ('Social Media', {
            'fields': ('twitter_url', 'linkedin_url', 'instagram_url', 'facebook_url')
        }),
        ('Copyright', {
            'fields': ('copyright_text',)
        })
    )
    
    list_display = ('company_name', 'email', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow adding if no instance exists
        return not Footer.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False

@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ('page_name', 'page_title', 'updated_at')
    list_filter = ('page_name', 'created_at')
    search_fields = ('page_title', 'page_subtitle')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Page Information', {
            'fields': ('page_name', 'page_title', 'page_subtitle')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'work_email', 'hotel_name', 'subject', 'number_of_rooms', 'created_at', 'is_processed')
    list_filter = ('subject', 'number_of_rooms', 'hear_about_us', 'is_processed', 'created_at')
    search_fields = ('full_name', 'work_email', 'hotel_name', 'job_title')
    readonly_fields = ('created_at',)
    list_editable = ('is_processed',)
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'work_email', 'phone_number')
        }),
        ('Business Details', {
            'fields': ('hotel_name', 'job_title', 'number_of_rooms')
        }),
        ('Inquiry', {
            'fields': ('subject', 'message', 'hear_about_us')
        }),
        ('Consent & Processing', {
            'fields': ('privacy_consent', 'is_processed', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_processed']
    
    def mark_as_processed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_processed=True, processed_at=timezone.now())
        self.message_user(request, f'{updated} inquiries marked as processed.')
    mark_as_processed.short_description = 'Mark selected inquiries as processed'

# Unregister the default Group admin_dashboard to prevent conflicts
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
