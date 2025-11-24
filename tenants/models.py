from django.db import models
import uuid

class SubscriptionPlan(models.Model):
    """Subscription plans for hotels"""
    plan_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_free_trial = models.BooleanField(default=False, help_text='Free trial plan with booking restrictions')
    max_rooms = models.PositiveIntegerField(default=50)
    max_managers = models.PositiveIntegerField(default=5)
    max_reports = models.PositiveIntegerField(default=10)
    
    # Feature flags
    has_advanced_analytics = models.BooleanField(default=False, help_text='Advanced Analytics feature')
    has_priority_support = models.BooleanField(default=False, help_text='24/7 Priority Support feature')
    
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True, help_text='Soft delete timestamp')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"