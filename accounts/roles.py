"""
Role-based access control system for hotel management
"""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

class RoleManager:
    """Manages roles and permissions for the hotel management system"""
    
    ROLES = {
        'SUPER_ADMIN': 'Super Admin',
        'HOTEL_OWNER': 'Hotel Owner',
        'HOTEL_MANAGER': 'Hotel Manager', 
        'FRONT_DESK': 'Front Desk Staff',
        'HOUSEKEEPING': 'Housekeeping Staff',
        'MAINTENANCE': 'Maintenance Staff',
        'KITCHEN_STAFF': 'Kitchen Staff',
        'ACCOUNTANT': 'Accountant',
    }
    
    PERMISSIONS = {
        'SUPER_ADMIN': [
            # Full system access
            'view_all_tenants',
            'manage_tenants',
            'manage_subscriptions',
            'view_system_analytics',
            'manage_system_settings',
        ],
        'HOTEL_OWNER': [
            # Property management
            'view_properties',
            'add_property',
            'change_property',
            'delete_property',
            # Staff management
            'view_staff',
            'add_staff',
            'change_staff',
            'delete_staff',
            # Full access to their properties
            'view_reservations',
            'add_reservation',
            'change_reservation',
            'delete_reservation',
            'view_guests',
            'add_guest',
            'change_guest',
            'view_billing',
            'manage_billing',
            'view_reports',
            'manage_settings',
        ],
        'HOTEL_MANAGER': [
            # Property operations
            'view_properties',
            'change_property',
            # Staff management (limited)
            'view_staff',
            'add_staff',
            'change_staff',
            # Reservations
            'view_reservations',
            'add_reservation',
            'change_reservation',
            'view_guests',
            'add_guest',
            'change_guest',
            # Operations
            'view_housekeeping',
            'manage_housekeeping',
            'view_maintenance',
            'manage_maintenance',
            'view_billing',
            'view_reports',
        ],
        'FRONT_DESK': [
            # Guest services
            'view_reservations',
            'add_reservation',
            'change_reservation',
            'view_guests',
            'add_guest',
            'change_guest',
            # Check-in/out
            'checkin_guest',
            'checkout_guest',
            # Basic billing
            'view_billing',
            'process_payment',
            # Room status
            'view_rooms',
            'change_room_status',
        ],
        'HOUSEKEEPING': [
            # Housekeeping tasks
            'view_housekeeping',
            'change_housekeeping_task',
            'view_rooms',
            'change_room_status',
            # Maintenance reporting
            'add_maintenance_issue',
        ],
        'MAINTENANCE': [
            # Maintenance tasks
            'view_maintenance',
            'change_maintenance_issue',
            'view_rooms',
            # Inventory (if applicable)
            'view_inventory',
            'change_inventory',
        ],
        'KITCHEN_STAFF': [
            # POS and food service
            'view_pos_orders',
            'change_pos_order',
            'view_pos_items',
            'add_pos_order',
            # Inventory
            'view_inventory',
            'change_inventory',
        ],
        'ACCOUNTANT': [
            # Financial management
            'view_billing',
            'manage_billing',
            'view_payments',
            'manage_payments',
            'view_reports',
            'generate_reports',
        ],
    }
    
    @classmethod
    def create_roles_and_permissions(cls):
        """Create all roles and assign permissions"""
        for role_key, role_name in cls.ROLES.items():
            group, created = Group.objects.get_or_create(name=role_name)
            
            # Get permissions for this role
            role_permissions = cls.PERMISSIONS.get(role_key, [])
            
            for perm_codename in role_permissions:
                # Create custom permission if it doesn't exist
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                except Permission.DoesNotExist:
                    # Create custom permission
                    content_type = ContentType.objects.get_for_model(Group)
                    permission = Permission.objects.create(
                        codename=perm_codename,
                        name=perm_codename.replace('_', ' ').title(),
                        content_type=content_type,
                    )
                
                group.permissions.add(permission)
    
    @classmethod
    def assign_role_to_user(cls, user, role_key):
        """Assign a role to a user"""
        if role_key not in cls.ROLES:
            raise ValueError(f"Invalid role: {role_key}")
        
        role_name = cls.ROLES[role_key]
        group = Group.objects.get(name=role_name)
        user.groups.add(group)
        
        # Update user flags based on role
        if role_key == 'SUPER_ADMIN':
            user.is_superuser = True
            user.is_staff = True
            user.save()
    
    @classmethod
    def get_user_role(cls, user):
        """Get the primary role of a user"""
        # Check superuser status first
        if user.is_superuser or (hasattr(user, 'role') and user.role == 'super_admin'):
            return 'SUPER_ADMIN'
        
        # Check role field if it exists
        if hasattr(user, 'role') and user.role:
            role_mapping = {
                'super_admin': 'SUPER_ADMIN',
                'Owner': 'HOTEL_OWNER',
                'Manager': 'HOTEL_MANAGER',
                'Staff': 'FRONT_DESK',
                'hotel_owner': 'HOTEL_OWNER',
                'hotel_manager': 'HOTEL_MANAGER',
                'front_desk': 'FRONT_DESK',
                'housekeeping': 'HOUSEKEEPING',
                'maintenance': 'MAINTENANCE',
                'kitchen_staff': 'KITCHEN_STAFF',
                'accountant': 'ACCOUNTANT',
                'employee': 'EMPLOYEE',
            }
            return role_mapping.get(user.role, 'EMPLOYEE')
        
        # Fallback to group-based role detection
        elif user.groups.filter(name='Hotel Owner').exists():
            return 'HOTEL_OWNER'
        elif user.groups.filter(name='Hotel Manager').exists():
            return 'HOTEL_MANAGER'
        elif user.groups.filter(name='Front Desk Staff').exists():
            return 'FRONT_DESK'
        elif user.groups.filter(name='Housekeeping Staff').exists():
            return 'HOUSEKEEPING'
        elif user.groups.filter(name='Maintenance Staff').exists():
            return 'MAINTENANCE'
        elif user.groups.filter(name='Kitchen Staff').exists():
            return 'KITCHEN_STAFF'
        elif user.groups.filter(name='Accountant').exists():
            return 'ACCOUNTANT'
        else:
            return 'EMPLOYEE'
    
    @classmethod
    def user_has_permission(cls, user, permission):
        """Check if user has a specific permission"""
        return user.has_perm(f'auth.{permission}') or user.user_permissions.filter(codename=permission).exists()