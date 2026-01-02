def site_config(request):
    """Basic site configuration context"""
    return {
        'site_name': 'AuraStay',
        'site_description': 'Hotel Management System'
    }

def user_permissions(request):
    """Context processor to add user permissions to all templates"""
    if not request.user.is_authenticated:
        return {}
    
    user = request.user
    
    # If superuser, grant all permissions
    if user.is_superuser:
        return {
            'can_view_hotels': True,
            'can_create_hotels': True,
            'can_edit_hotels': True,
            'can_delete_hotels': True,
            'can_view_rooms': True,
            'can_create_rooms': True,
            'can_edit_rooms': True,
            'can_delete_rooms': True,
            'can_view_staff': True,
            'can_create_staff': True,
            'can_edit_staff': True,
            'can_delete_staff': True,
            'can_view_reservations': True,
            'can_create_reservations': True,
            'can_edit_reservations': True,
            'can_delete_reservations': True,
            'can_view_guests': True,
            'can_create_guests': True,
            'can_edit_guests': True,
            'can_delete_guests': True,
            'can_view_companies': True,
            'can_create_companies': True,
            'can_edit_companies': True,
            'can_delete_companies': True,
            'can_view_front_desk': True,
            'can_view_housekeeping': True,
            'can_view_maintenance': True,
            'can_view_pos': True,
            'can_view_inventory': True,
            'can_view_billing': True,
            'can_view_payments': True,
            'can_view_reports': True,
            'can_view_configurations': True,
        }
    
    # Get user permissions from employee profile
    permissions = {}
    
    try:
        employee = user.employee_profile
        
        # Hotel permissions
        permissions['can_view_hotels'] = employee.can_view_hotels
        permissions['can_create_hotels'] = employee.can_create_hotels
        permissions['can_edit_hotels'] = employee.can_edit_hotels
        permissions['can_delete_hotels'] = employee.can_delete_hotels
        
        # Room permissions
        permissions['can_view_rooms'] = employee.can_view_rooms
        permissions['can_create_rooms'] = employee.can_create_rooms
        permissions['can_edit_rooms'] = employee.can_edit_rooms
        permissions['can_delete_rooms'] = employee.can_delete_rooms
        
        # Staff permissions
        permissions['can_view_staff'] = employee.can_view_staff
        permissions['can_create_staff'] = employee.can_create_staff
        permissions['can_edit_staff'] = employee.can_edit_staff
        permissions['can_delete_staff'] = employee.can_delete_staff
        
        # Reservation permissions
        permissions['can_view_reservations'] = employee.can_view_reservations
        permissions['can_create_reservations'] = employee.can_create_reservations
        permissions['can_edit_reservations'] = employee.can_edit_reservations
        permissions['can_delete_reservations'] = employee.can_delete_reservations
        
        # Guest permissions
        permissions['can_view_guests'] = employee.can_view_guests
        permissions['can_create_guests'] = employee.can_create_guests
        permissions['can_edit_guests'] = employee.can_edit_guests
        permissions['can_delete_guests'] = employee.can_delete_guests
        
        # Company permissions
        permissions['can_view_companies'] = employee.can_view_companies
        permissions['can_create_companies'] = employee.can_create_companies
        permissions['can_edit_companies'] = employee.can_edit_companies
        permissions['can_delete_companies'] = employee.can_delete_companies
        
        # Module permissions
        permissions['can_view_front_desk'] = employee.can_view_front_desk
        permissions['can_view_housekeeping'] = employee.can_view_housekeeping
        permissions['can_view_maintenance'] = employee.can_view_maintenance
        permissions['can_view_pos'] = employee.can_view_pos
        permissions['can_view_inventory'] = employee.can_view_inventory
        permissions['can_view_billing'] = employee.can_view_billing
        permissions['can_view_payments'] = employee.can_view_payments
        permissions['can_view_reports'] = employee.can_view_reports
        permissions['can_view_configurations'] = employee.can_view_configurations
        permissions['can_create_configurations'] = employee.can_add_configurations
        permissions['can_edit_configurations'] = employee.can_change_configurations
        permissions['can_delete_configurations'] = employee.can_delete_configurations
        
    except:
        # If no employee profile, check role and grant appropriate permissions
        if hasattr(user, 'role'):
            if user.role == 'Maintenance':
                permissions = {
                    'can_view_hotels': False,
                    'can_create_hotels': False,
                    'can_edit_hotels': False,
                    'can_delete_hotels': False,
                    'can_view_rooms': True,  # Can view room details
                    'can_create_rooms': False,
                    'can_edit_rooms': False,
                    'can_delete_rooms': False,
                    'can_view_staff': False,
                    'can_create_staff': False,
                    'can_edit_staff': False,
                    'can_delete_staff': False,
                    'can_view_reservations': False,
                    'can_create_reservations': False,
                    'can_edit_reservations': False,
                    'can_delete_reservations': False,
                    'can_view_guests': False,  # Restricted: Guest data
                    'can_create_guests': False,
                    'can_edit_guests': False,
                    'can_delete_guests': False,
                    'can_view_companies': False,
                    'can_create_companies': False,
                    'can_edit_companies': False,
                    'can_delete_companies': False,
                    'can_view_front_desk': False,
                    'can_view_housekeeping': False,
                    'can_view_maintenance': True,  # Full maintenance access
                    'can_view_pos': False,
                    'can_view_inventory': False,  # Removed: No inventory access
                    'can_view_billing': False,  # Restricted: Financial operations
                    'can_view_payments': False,  # Restricted: Financial operations
                    'can_view_reports': False,
                    'can_view_configurations': False,
                }
            elif user.role == 'Accountant':
                permissions = {
                    'can_view_hotels': False,
                    'can_create_hotels': False,
                    'can_edit_hotels': False,
                    'can_delete_hotels': False,
                    'can_view_rooms': False,  # Restricted: Room operations
                    'can_create_rooms': False,
                    'can_edit_rooms': False,
                    'can_delete_rooms': False,
                    'can_view_staff': False,  # Restricted: Staff management
                    'can_create_staff': False,
                    'can_edit_staff': False,
                    'can_delete_staff': False,
                    'can_view_reservations': True,  # Financial data only
                    'can_create_reservations': False,
                    'can_edit_reservations': False,
                    'can_delete_reservations': False,
                    'can_view_guests': False,  # Restricted: Guest management
                    'can_create_guests': False,
                    'can_edit_guests': False,
                    'can_delete_guests': False,
                    'can_view_companies': False,
                    'can_create_companies': False,
                    'can_edit_companies': False,
                    'can_delete_companies': False,
                    'can_view_front_desk': False,
                    'can_view_housekeeping': False,
                    'can_view_maintenance': False,
                    'can_view_pos': True,  # POS transactions
                    'can_view_inventory': False,
                    'can_view_billing': True,  # CRUD on Billing
                    'can_view_payments': True,  # CRUD on Payments
                    'can_view_reports': True,  # Financial reports
                    'can_view_configurations': False,  # Restricted: Hotel configuration
                }
            elif user.role == 'Staff':
                permissions = {
                    'can_view_hotels': True,  # Basic hotel info only
                    'can_create_hotels': False,
                    'can_edit_hotels': False,
                    'can_delete_hotels': False,
                    'can_view_rooms': False,
                    'can_create_rooms': False,
                    'can_edit_rooms': False,
                    'can_delete_rooms': False,
                    'can_view_staff': False,  # Restricted: Staff management
                    'can_create_staff': False,
                    'can_edit_staff': False,
                    'can_delete_staff': False,
                    'can_view_reservations': False,
                    'can_create_reservations': False,
                    'can_edit_reservations': False,
                    'can_delete_reservations': False,
                    'can_view_guests': False,
                    'can_create_guests': False,
                    'can_edit_guests': False,
                    'can_delete_guests': False,
                    'can_view_companies': False,
                    'can_create_companies': False,
                    'can_edit_companies': False,
                    'can_delete_companies': False,
                    'can_view_front_desk': False,
                    'can_view_housekeeping': True,  # View assigned schedules
                    'can_view_maintenance': False,
                    'can_view_pos': False,
                    'can_view_inventory': False,
                    'can_view_billing': False,  # Restricted: Financial data
                    'can_view_payments': False,  # Restricted: Financial data
                    'can_view_reports': False,  # Restricted: Financial data
                    'can_view_configurations': False,
                }
            else:
                # Default permissions for other roles
                permissions = {
                    'can_view_hotels': True,
                    'can_create_hotels': True,
                    'can_edit_hotels': True,
                    'can_delete_hotels': True,
                    'can_view_rooms': True,
                    'can_create_rooms': True,
                    'can_edit_rooms': True,
                    'can_delete_rooms': True,
                    'can_view_staff': True,
                    'can_create_staff': True,
                    'can_edit_staff': True,
                    'can_delete_staff': True,
                    'can_view_reservations': True,
                    'can_create_reservations': True,
                    'can_edit_reservations': True,
                    'can_delete_reservations': True,
                    'can_view_guests': True,
                    'can_create_guests': True,
                    'can_edit_guests': True,
                    'can_delete_guests': True,
                    'can_view_companies': True,
                    'can_create_companies': True,
                    'can_edit_companies': True,
                    'can_delete_companies': True,
                    'can_view_front_desk': True,
                    'can_view_housekeeping': True,
                    'can_view_maintenance': True,
                    'can_view_pos': True,
                    'can_view_inventory': True,
                    'can_view_billing': True,
                    'can_view_payments': True,
                    'can_view_reports': True,
                    'can_view_configurations': True,
                }
        else:
            # If no employee profile or owner, grant basic permissions
            permissions = {
                'can_view_hotels': True,
                'can_create_hotels': True,
                'can_edit_hotels': True,
                'can_delete_hotels': True,
                'can_view_rooms': True,
                'can_create_rooms': True,
                'can_edit_rooms': True,
                'can_delete_rooms': True,
                'can_view_staff': True,
                'can_create_staff': True,
                'can_edit_staff': True,
                'can_delete_staff': True,
                'can_view_reservations': True,
                'can_create_reservations': True,
                'can_edit_reservations': True,
                'can_delete_reservations': True,
                'can_view_guests': True,
                'can_create_guests': True,
                'can_edit_guests': True,
                'can_delete_guests': True,
                'can_view_companies': True,
                'can_create_companies': True,
                'can_edit_companies': True,
                'can_delete_companies': True,
                'can_view_front_desk': True,
                'can_view_housekeeping': True,
                'can_view_maintenance': True,
                'can_view_pos': True,
                'can_view_inventory': True,
                'can_view_billing': True,
                'can_view_payments': True,
                'can_view_reports': True,
                'can_view_configurations': True,
            }
    
    return permissions