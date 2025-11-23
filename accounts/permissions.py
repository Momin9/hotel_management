from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Default permissions for different roles
DEFAULT_PERMISSIONS = {
    'Manager': [
        'view_hotel', 'change_hotel', 'view_room', 'add_room', 'change_room',
        'view_reservation', 'add_reservation', 'change_reservation', 'delete_reservation',
        'view_guest', 'add_guest', 'change_guest', 'view_staff', 'add_staff', 'change_staff',
        'view_reports', 'view_billing', 'view_maintenance', 'add_maintenance', 'change_maintenance'
    ],
    'Staff': [
        'view_hotel', 'view_room', 'view_reservation', 'view_guest', 'add_guest', 'change_guest'
    ],
    'Receptionist': [
        'view_hotel', 'view_room', 'view_reservation', 'add_reservation', 'change_reservation',
        'view_guest', 'add_guest', 'change_guest', 'view_checkin', 'add_checkin', 'change_checkin'
    ],
    'Housekeeper': [
        'view_hotel', 'view_room', 'change_room', 'view_housekeeping', 'add_housekeeping', 'change_housekeeping'
    ],
    'Maintenance': [
        'view_hotel', 'view_room', 'view_maintenance', 'add_maintenance', 'change_maintenance', 'delete_maintenance'
    ],
    'Kitchen': [
        'view_hotel', 'view_pos', 'add_pos', 'change_pos', 'view_inventory', 'change_inventory'
    ],
    'Accountant': [
        'view_hotel', 'view_billing', 'add_billing', 'change_billing', 'view_reports', 'view_payment'
    ]
}

# Permission categories for UI
PERMISSION_CATEGORIES = {
    'Hotel Management': [
        ('view_hotel', 'View Hotel Information'),
        ('change_hotel', 'Edit Hotel Settings'),
        ('view_room', 'View Rooms'),
        ('add_room', 'Add New Rooms'),
        ('change_room', 'Edit Room Details'),
        ('delete_room', 'Delete Rooms'),
    ],
    'Reservations': [
        ('view_reservation', 'View Reservations'),
        ('add_reservation', 'Create Reservations'),
        ('change_reservation', 'Edit Reservations'),
        ('delete_reservation', 'Cancel Reservations'),
        ('view_checkin', 'View Check-ins'),
        ('add_checkin', 'Process Check-ins'),
        ('change_checkin', 'Modify Check-ins'),
    ],
    'Guest Management': [
        ('view_guest', 'View Guest Profiles'),
        ('add_guest', 'Add New Guests'),
        ('change_guest', 'Edit Guest Information'),
        ('delete_guest', 'Delete Guest Profiles'),
    ],
    'Staff Management': [
        ('view_staff', 'View Staff List'),
        ('add_staff', 'Add New Staff'),
        ('change_staff', 'Edit Staff Details'),
        ('delete_staff', 'Remove Staff'),
    ],
    'Housekeeping': [
        ('view_housekeeping', 'View Housekeeping Tasks'),
        ('add_housekeeping', 'Create Housekeeping Tasks'),
        ('change_housekeeping', 'Update Task Status'),
        ('delete_housekeeping', 'Delete Tasks'),
    ],
    'Maintenance': [
        ('view_maintenance', 'View Maintenance Issues'),
        ('add_maintenance', 'Report New Issues'),
        ('change_maintenance', 'Update Issue Status'),
        ('delete_maintenance', 'Close Issues'),
    ],
    'Point of Sale': [
        ('view_pos', 'View POS Orders'),
        ('add_pos', 'Create Orders'),
        ('change_pos', 'Modify Orders'),
        ('delete_pos', 'Cancel Orders'),
    ],
    'Inventory': [
        ('view_inventory', 'View Inventory'),
        ('add_inventory', 'Add Inventory Items'),
        ('change_inventory', 'Update Inventory'),
        ('delete_inventory', 'Remove Items'),
    ],
    'Financial': [
        ('view_billing', 'View Billing Information'),
        ('add_billing', 'Create Invoices'),
        ('change_billing', 'Edit Billing'),
        ('view_payment', 'View Payments'),
        ('add_payment', 'Process Payments'),
        ('view_reports', 'View Financial Reports'),
    ]
}

def get_default_permissions_for_role(role):
    """Get default permissions for a role"""
    return DEFAULT_PERMISSIONS.get(role, [])

def get_permission_categories():
    """Get all permission categories for UI"""
    return PERMISSION_CATEGORIES

def assign_default_permissions(user):
    """Assign default permissions to a user based on their role"""
    if not user.role:
        return
    
    default_perms = get_default_permissions_for_role(user.role)
    
    # Clear existing permissions
    user.user_permissions.clear()
    
    # Assign default permissions
    for perm_codename in default_perms:
        try:
            permission = Permission.objects.get(codename=perm_codename)
            user.user_permissions.add(permission)
        except Permission.DoesNotExist:
            # Create custom permission if it doesn't exist
            content_type = ContentType.objects.get_for_model(user)
            permission = Permission.objects.create(
                codename=perm_codename,
                name=perm_codename.replace('_', ' ').title(),
                content_type=content_type
            )
            user.user_permissions.add(permission)

def check_user_permission(user, permission_codename):
    """Check if user has specific permission"""
    if user.is_superuser:
        return True
    
    if user.role == 'Owner':
        return True  # Hotel owners have all permissions for their hotels
    
    return user.has_perm(f'auth.{permission_codename}') or user.user_permissions.filter(codename=permission_codename).exists()

def get_user_permissions(user):
    """Get all permissions for a user"""
    if user.is_superuser or user.role == 'Owner':
        # Return all permissions for superusers and owners
        all_perms = []
        for category_perms in PERMISSION_CATEGORIES.values():
            all_perms.extend([perm[0] for perm in category_perms])
        return all_perms
    
    return list(user.user_permissions.values_list('codename', flat=True))