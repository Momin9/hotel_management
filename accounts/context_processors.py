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