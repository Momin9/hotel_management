"""
Custom decorators for role-based access control
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from .roles import RoleManager

def role_required(*allowed_roles):
    """
    Decorator to restrict access to specific roles
    Usage: @role_required('HOTEL_OWNER', 'HOTEL_MANAGER')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user_role = RoleManager.get_user_role(request.user)
            
            if user_role not in allowed_roles:
                messages.error(request, f'Access denied. Required roles: {", ".join(allowed_roles)}. Your role: {user_role}')
                # Redirect to appropriate dashboard based on actual role
                if user_role == 'SUPER_ADMIN':
                    return redirect('accounts:super_admin_dashboard')
                elif user_role in ['HOTEL_OWNER', 'HOTEL_MANAGER']:
                    return redirect('accounts:owner_dashboard')
                elif user_role in ['FRONT_DESK', 'HOUSEKEEPING', 'MAINTENANCE', 'KITCHEN_STAFF', 'ACCOUNTANT']:
                    return redirect('accounts:employee_dashboard')
                else:
                    return redirect('accounts:login')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def permission_required(permission):
    """
    Decorator to check specific permissions
    Usage: @permission_required('view_reservations')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not RoleManager.user_has_permission(request.user, permission):
                messages.error(request, 'You do not have permission to perform this action.')
                user_role = RoleManager.get_user_role(request.user)
                if user_role == 'SUPER_ADMIN':
                    return redirect('accounts:super_admin_dashboard')
                elif user_role in ['HOTEL_OWNER', 'HOTEL_MANAGER']:
                    return redirect('accounts:owner_dashboard')
                elif user_role in ['FRONT_DESK', 'HOUSEKEEPING', 'MAINTENANCE', 'KITCHEN_STAFF', 'ACCOUNTANT']:
                    return redirect('accounts:employee_dashboard')
                else:
                    return redirect('accounts:login')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def super_admin_required(view_func):
    """Decorator for super admin only views"""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'Super admin access required.')
            user_role = RoleManager.get_user_role(request.user)
            if user_role in ['HOTEL_OWNER', 'HOTEL_MANAGER']:
                return redirect('accounts:owner_dashboard')
            elif user_role in ['FRONT_DESK', 'HOUSEKEEPING', 'MAINTENANCE', 'KITCHEN_STAFF', 'ACCOUNTANT']:
                return redirect('accounts:employee_dashboard')
            else:
                return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def hotel_owner_required(view_func):
    """Decorator for hotel owner only views"""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        user_role = RoleManager.get_user_role(request.user)
        if not (user_role in ['HOTEL_OWNER', 'SUPER_ADMIN']):
            messages.error(request, 'Hotel owner access required.')
            if user_role == 'SUPER_ADMIN':
                return redirect('accounts:super_admin_dashboard')
            elif user_role in ['FRONT_DESK', 'HOUSEKEEPING', 'MAINTENANCE', 'KITCHEN_STAFF', 'ACCOUNTANT']:
                return redirect('accounts:employee_dashboard')
            else:
                return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view