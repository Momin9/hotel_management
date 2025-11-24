from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .permissions import check_user_permission

def permission_required(permission_codename, raise_exception=False):
    """
    Decorator to check if user has specific permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            # Check permission
            if not check_user_permission(request.user, permission_codename):
                if raise_exception:
                    raise PermissionDenied(f"You don't have permission to {permission_codename.replace('_', ' ')}")
                else:
                    messages.error(request, f"You don't have permission to {permission_codename.replace('_', ' ')}")
                    return redirect('accounts:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def any_permission_required(*permission_codenames, raise_exception=False):
    """
    Decorator to check if user has any of the specified permissions
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            # Check if user has any of the permissions
            has_permission = any(
                check_user_permission(request.user, perm) 
                for perm in permission_codenames
            )
            
            if not has_permission:
                if raise_exception:
                    raise PermissionDenied("You don't have permission to access this resource")
                else:
                    messages.error(request, "You don't have permission to access this resource")
                    return redirect('accounts:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def owner_or_permission_required(permission_codename, raise_exception=False):
    """
    Decorator to check if user is owner or has specific permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            # Owners and superusers always have access
            if request.user.role == 'Owner' or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check permission for staff
            if not check_user_permission(request.user, permission_codename):
                if raise_exception:
                    raise PermissionDenied(f"You don't have permission to {permission_codename.replace('_', ' ')}")
                else:
                    messages.error(request, f"You don't have permission to {permission_codename.replace('_', ' ')}")
                    return redirect('accounts:dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def super_admin_required(view_func):
    """Decorator to require super admin access"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        from .roles import RoleManager
        user_role = RoleManager.get_user_role(request.user)
        if user_role != 'SUPER_ADMIN':
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('accounts:dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view