from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, Payment

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['timestamp']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'guest_name', 'total_amount_formatted', 'status_badge', 'due_date', 'created_at']
    list_filter = ['status', 'created_at', 'due_date']
    search_fields = ['invoice_number', 'guest__first_name', 'guest__last_name']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
    inlines = [PaymentInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'guest', 'status')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'total_amount', 'paid_amount')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        })
    )
    
    def guest_name(self, obj):
        return obj.guest.full_name if obj.guest else "No Guest"
    guest_name.short_description = 'Guest'
    
    def total_amount_formatted(self, obj):
        return f"${obj.total_amount}"
    total_amount_formatted.short_description = 'Total'
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6B7280',
            'pending': '#F59E0B',
            'paid': '#10B981',
            'overdue': '#EF4444',
            'cancelled': '#EF4444'
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = ['mark_as_paid', 'mark_as_overdue']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
        self.message_user(request, f'{queryset.count()} invoices marked as paid.')
    mark_as_paid.short_description = 'Mark as Paid'
    
    def mark_as_overdue(self, request, queryset):
        queryset.update(status='overdue')
        self.message_user(request, f'{queryset.count()} invoices marked as overdue.')
    mark_as_overdue.short_description = 'Mark as Overdue'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount_formatted', 'method_badge', 'status_badge', 'timestamp']
    list_filter = ['method', 'status', 'timestamp']
    search_fields = ['invoice__invoice_number', 'reference_number']
    readonly_fields = ['timestamp']
    
    def amount_formatted(self, obj):
        return f"${obj.amount}"
    amount_formatted.short_description = 'Amount'
    
    def method_badge(self, obj):
        colors = {
            'cash': '#10B981',
            'card': '#3B82F6',
            'bank_transfer': '#8B5CF6',
            'digital_wallet': '#F59E0B'
        }
        color = colors.get(obj.method, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_method_display()
        )
    method_badge.short_description = 'Method'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#F59E0B',
            'completed': '#10B981',
            'failed': '#EF4444',
            'refunded': '#6B7280'
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'