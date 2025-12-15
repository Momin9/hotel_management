"""
Role-based permission assignments for hotel management system
"""

def get_housekeeper_permissions():
    """Get permissions for Housekeeping staff"""
    return {
        # Room Management
        'can_view_rooms': True,
        'can_view_room_status': True,
        'can_update_room_status': True,
        
        # Housekeeping
        'can_view_housekeeping': True,
        'can_change_housekeeping': True,
        'can_view_housekeeping_schedule': True,
        'can_view_room_assignments': True,
        
        # Maintenance
        'can_request_maintenance': True,
        'can_view_maintenance': True,
        
        # Restricted permissions
        'can_view_billing': False,
        'can_view_payments': False,
        'can_view_guests': False,
        'can_view_reservations': False,
        'can_view_staff': False,
        'can_view_reports': False,
    }

def apply_housekeeper_permissions(user):
    """Apply housekeeper permissions to user"""
    if user.role == 'Housekeeping':
        permissions = get_housekeeper_permissions()
        for perm, value in permissions.items():
            if hasattr(user, perm):
                setattr(user, perm, value)
        user.save()
        return True
    return False