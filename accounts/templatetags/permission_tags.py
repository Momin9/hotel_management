from django import template
from accounts.permissions import check_user_permission

register = template.Library()

@register.filter
def has_permission(user, permission_codename):
    """Check if user has specific permission"""
    return check_user_permission(user, permission_codename)

@register.simple_tag
def user_can(user, permission_codename):
    """Template tag to check user permission"""
    return check_user_permission(user, permission_codename)