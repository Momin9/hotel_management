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
    'Housekeeping': [
        'view_rooms', 'change_rooms', 'view_housekeeping', 'change_housekeeping', 'add_maintenance'
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
    ],
    'Company Management': [
        ('view_companies', 'View Company Contracts'),
        ('add_companies', 'Create Company Contracts'),
        ('change_companies', 'Edit Company Contracts'),
        ('delete_companies', 'Delete Company Contracts'),
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
    
    # Get or create content type for custom permissions
    content_type = ContentType.objects.get_for_model(user)
    
    # Assign default permissions
    for perm_codename in default_perms:
        try:
            # Try to find existing permission, get first one if multiple exist
            permission = Permission.objects.filter(codename=perm_codename).first()
            if not permission:
                # Create custom permission if it doesn't exist
                permission = Permission.objects.create(
                    codename=perm_codename,
                    name=perm_codename.replace('_', ' ').title(),
                    content_type=content_type
                )
        except Exception:
            # Skip if there's any error with this permission
            continue
        
        if permission:
            user.user_permissions.add(permission)

def check_user_permission(user, permission_codename):
    """Check if user has specific permission"""
    if user.is_superuser:
        return True
    
    if user.role == 'Owner':
        return True  # Hotel owners have all permissions for their hotels
    
    # Map permission codenames to boolean fields on User model
    permission_field_map = {
        # Configuration permissions
        'view_configurations': 'can_view_configurations',
        'add_configurations': 'can_add_configurations',
        'change_configurations': 'can_change_configurations',
        'delete_configurations': 'can_delete_configurations',
        
        # Staff permissions
        'view_staff': 'can_view_staff',
        'add_staff': 'can_add_staff',
        'change_staff': 'can_change_staff',
        'delete_staff': 'can_delete_staff',
        
        # Hotel permissions
        'view_hotels': 'can_view_hotels',
        'change_hotels': 'can_change_hotels',
        'view_rooms': 'can_view_rooms',
        'add_rooms': 'can_add_rooms',
        'change_rooms': 'can_change_rooms',
        'delete_rooms': 'can_delete_rooms',
        
        # Reservation permissions
        'view_reservations': 'can_view_reservations',
        'add_reservations': 'can_add_reservations',
        'change_reservations': 'can_change_reservations',
        'delete_reservations': 'can_delete_reservations',
        'view_checkins': 'can_view_checkins',
        'add_checkins': 'can_add_checkins',
        'change_checkins': 'can_change_checkins',
        
        # Guest permissions
        'view_guests': 'can_view_guests',
        'add_guests': 'can_add_guests',
        'change_guests': 'can_change_guests',
        'delete_guests': 'can_delete_guests',
        
        # Operations permissions
        'view_housekeeping': 'can_view_housekeeping',
        'add_housekeeping': 'can_add_housekeeping',
        'change_housekeeping': 'can_change_housekeeping',
        'delete_housekeeping': 'can_delete_housekeeping',
        
        'view_maintenance': 'can_view_maintenance',
        'add_maintenance': 'can_add_maintenance',
        'change_maintenance': 'can_change_maintenance',
        'delete_maintenance': 'can_delete_maintenance',
        
        'view_pos': 'can_view_pos',
        'add_pos': 'can_add_pos',
        'change_pos': 'can_change_pos',
        'delete_pos': 'can_delete_pos',
        
        # Financial permissions
        'view_billing': 'can_view_billing',
        'add_billing': 'can_add_billing',
        'change_billing': 'can_change_billing',
        'view_payments': 'can_view_payments',
        'add_payments': 'can_add_payments',
        'view_reports': 'can_view_reports',
        
        # Inventory permissions
        'view_inventory': 'can_view_inventory',
        'add_inventory': 'can_add_inventory',
        'change_inventory': 'can_change_inventory',
        'delete_inventory': 'can_delete_inventory',
        
        # Company permissions
        'view_companies': 'can_view_companies',
        'add_companies': 'can_add_companies',
        'change_companies': 'can_change_companies',
        'delete_companies': 'can_delete_companies',
    }
    
    # Get the boolean field name for this permission
    field_name = permission_field_map.get(permission_codename)
    if field_name and hasattr(user, field_name):
        return getattr(user, field_name)
    
    # Fallback to Django permissions if no boolean field mapping exists
    return user.user_permissions.filter(codename=permission_codename).exists()

def get_user_permissions(user):
    """Get all permissions for a user"""
    if user.is_superuser or user.role == 'Owner':
        # Return all permissions for superusers and owners
        all_perms = []
        for category_perms in PERMISSION_CATEGORIES.values():
            all_perms.extend([perm[0] for perm in category_perms])
        return all_perms
    
    return list(user.user_permissions.values_list('codename', flat=True))