"""
Role-based permissions system for hotel management
"""

class RolePermissions:
    """Define permissions for each role"""
    
    ROLE_PERMISSIONS = {
        'Owner': {
            # Full access to everything
            'can_view_hotels': True,
            'can_change_hotels': True,
            'can_view_rooms': True,
            'can_add_rooms': True,
            'can_change_rooms': True,
            'can_delete_rooms': True,
            'can_view_reservations': True,
            'can_add_reservations': True,
            'can_change_reservations': True,
            'can_delete_reservations': True,
            'can_view_checkins': True,
            'can_add_checkins': True,
            'can_change_checkins': True,
            'can_view_guests': True,
            'can_add_guests': True,
            'can_change_guests': True,
            'can_delete_guests': True,
            'can_view_staff': True,
            'can_add_staff': True,
            'can_change_staff': True,
            'can_delete_staff': True,
            'can_view_housekeeping': True,
            'can_add_housekeeping': True,
            'can_change_housekeeping': True,
            'can_delete_housekeeping': True,
            'can_view_maintenance': True,
            'can_add_maintenance': True,
            'can_change_maintenance': True,
            'can_delete_maintenance': True,
            'can_view_pos': True,
            'can_add_pos': True,
            'can_change_pos': True,
            'can_delete_pos': True,
            'can_view_inventory': True,
            'can_add_inventory': True,
            'can_change_inventory': True,
            'can_delete_inventory': True,
            'can_view_billing': True,
            'can_add_billing': True,
            'can_change_billing': True,
            'can_view_payments': True,
            'can_add_payments': True,
            'can_view_reports': True,
            'can_view_configurations': True,
            'can_add_configurations': True,
            'can_change_configurations': True,
            'can_delete_configurations': True,
            'can_view_companies': True,
            'can_add_companies': True,
            'can_change_companies': True,
            'can_delete_companies': True,
        },
        
        'Manager': {
            # Hotel Info (Read-only)
            'can_view_hotels': True,
            'can_change_hotels': False,
            # Staff Management (except owner/admin roles)
            'can_view_staff': True,
            'can_add_staff': True,
            'can_change_staff': True,
            'can_delete_staff': False,  # Limited
            # View/Approve Reservations
            'can_view_reservations': True,
            'can_add_reservations': False,
            'can_change_reservations': True,  # Approve
            'can_delete_reservations': False,
            # View Guest Management
            'can_view_guests': True,
            'can_add_guests': False,
            'can_change_guests': False,
            'can_delete_guests': False,
            # Company Contracts
            'can_view_companies': True,
            'can_add_companies': True,
            'can_change_companies': True,
            'can_delete_companies': True,
            # Rooms (limited)
            'can_view_rooms': True,
            'can_add_rooms': False,
            'can_change_rooms': True,
            'can_delete_rooms': False,
            # View all Reports
            'can_view_reports': True,
            # Approve Payments/Billing
            'can_view_billing': True,
            'can_add_billing': False,
            'can_change_billing': True,  # Approve
            'can_view_payments': True,
            'can_add_payments': True,  # Approve
            # View POS & Inventory
            'can_view_pos': True,
            'can_add_pos': False,
            'can_change_pos': False,
            'can_delete_pos': False,
            'can_view_inventory': True,
            'can_add_inventory': False,
            'can_change_inventory': False,
            'can_delete_inventory': False,
            # Housekeeping & Maintenance
            'can_view_housekeeping': True,
            'can_add_housekeeping': True,
            'can_change_housekeeping': True,
            'can_delete_housekeeping': True,
            'can_view_maintenance': True,
            'can_add_maintenance': True,
            'can_change_maintenance': True,
            'can_delete_maintenance': True,
            # No system settings
            'can_view_configurations': False,
            'can_add_configurations': False,
            'can_change_configurations': False,
            'can_delete_configurations': False,
            'can_view_checkins': True,
            'can_add_checkins': False,
            'can_change_checkins': False,
        },
        
        'Receptionist': {
            # View Hotel Info (Read-only)
            'can_view_hotels': True,
            'can_change_hotels': False,
            # CRUD on Reservations
            'can_view_reservations': True,
            'can_add_reservations': True,
            'can_change_reservations': True,
            'can_delete_reservations': True,
            # CRUD on Guest Management
            'can_view_guests': True,
            'can_add_guests': True,
            'can_change_guests': True,
            'can_delete_guests': True,
            # View Room Availability
            'can_view_rooms': True,
            'can_add_rooms': False,
            'can_change_rooms': False,
            'can_delete_rooms': False,
            # Check-in/Check-out operations
            'can_view_checkins': True,
            'can_add_checkins': True,
            'can_change_checkins': True,
            # Create/View Payments & Billing
            'can_view_billing': True,
            'can_add_billing': True,
            'can_change_billing': False,
            'can_view_payments': True,
            'can_add_payments': True,
            # View Company Contracts (Read-only)
            'can_view_companies': True,
            'can_add_companies': False,
            'can_change_companies': False,
            'can_delete_companies': False,
            # View Reports (Frontdesk related)
            'can_view_reports': True,
            # Restricted areas
            'can_view_staff': False,
            'can_add_staff': False,
            'can_change_staff': False,
            'can_delete_staff': False,
            'can_view_inventory': False,
            'can_add_inventory': False,
            'can_change_inventory': False,
            'can_delete_inventory': False,
            'can_view_configurations': False,
            'can_add_configurations': False,
            'can_change_configurations': False,
            'can_delete_configurations': False,
            'can_view_housekeeping': False,
            'can_add_housekeeping': False,
            'can_change_housekeeping': False,
            'can_delete_housekeeping': False,
            'can_view_maintenance': False,
            'can_add_maintenance': False,
            'can_change_maintenance': False,
            'can_delete_maintenance': False,
            'can_view_pos': False,
            'can_add_pos': False,
            'can_change_pos': False,
            'can_delete_pos': False,
        },
        
        'Housekeeping': {
            # View Room Status
            'can_view_rooms': True,
            'can_add_rooms': False,
            'can_change_rooms': True,  # Update room cleaning status
            'can_delete_rooms': False,
            # View Housekeeping Schedule
            'can_view_housekeeping': True,
            'can_add_housekeeping': False,
            'can_change_housekeeping': True,  # Update status
            'can_delete_housekeeping': False,
            # Request Maintenance for rooms
            'can_view_maintenance': True,
            'can_add_maintenance': True,  # Request maintenance
            'can_change_maintenance': False,
            'can_delete_maintenance': False,
            # View Room Assignments
            'can_view_checkins': True,
            'can_add_checkins': False,
            'can_change_checkins': False,
            # Restricted areas
            'can_view_hotels': False,
            'can_change_hotels': False,
            'can_view_reservations': False,
            'can_add_reservations': False,
            'can_change_reservations': False,
            'can_delete_reservations': False,
            'can_view_guests': False,
            'can_add_guests': False,
            'can_change_guests': False,
            'can_delete_guests': False,
            'can_view_staff': False,
            'can_add_staff': False,
            'can_change_staff': False,
            'can_delete_staff': False,
            'can_view_billing': False,
            'can_add_billing': False,
            'can_change_billing': False,
            'can_view_payments': False,
            'can_add_payments': False,
            'can_view_reports': False,
            'can_view_configurations': False,
            'can_add_configurations': False,
            'can_change_configurations': False,
            'can_delete_configurations': False,
            'can_view_companies': False,
            'can_add_companies': False,
            'can_change_companies': False,
            'can_delete_companies': False,
            'can_view_pos': False,
            'can_add_pos': False,
            'can_change_pos': False,
            'can_delete_pos': False,
            'can_view_inventory': False,
            'can_add_inventory': False,
            'can_change_inventory': False,
            'can_delete_inventory': False,
        },
        
        'Maintenance': {
            # View Maintenance Requests
            'can_view_maintenance': True,
            'can_add_maintenance': False,
            'can_change_maintenance': True,  # Update status
            'can_delete_maintenance': True,  # Complete/close
            # View Room/Facility details
            'can_view_rooms': True,
            'can_add_rooms': False,
            'can_change_rooms': False,
            'can_delete_rooms': False,
            # Inventory View (for parts/tools)
            'can_view_inventory': True,
            'can_add_inventory': False,
            'can_change_inventory': False,
            'can_delete_inventory': False,
            # Report completion
            'can_view_reports': True,  # Limited to maintenance reports
            # Restricted areas
            'can_view_hotels': False,
            'can_change_hotels': False,
            'can_view_reservations': False,
            'can_add_reservations': False,
            'can_change_reservations': False,
            'can_delete_reservations': False,
            'can_view_guests': False,
            'can_add_guests': False,
            'can_change_guests': False,
            'can_delete_guests': False,
            'can_view_staff': False,
            'can_add_staff': False,
            'can_change_staff': False,
            'can_delete_staff': False,
            'can_view_billing': False,
            'can_add_billing': False,
            'can_change_billing': False,
            'can_view_payments': False,
            'can_add_payments': False,
            'can_view_configurations': False,
            'can_add_configurations': False,
            'can_change_configurations': False,
            'can_delete_configurations': False,
            'can_view_companies': False,
            'can_add_companies': False,
            'can_change_companies': False,
            'can_delete_companies': False,
            'can_view_checkins': False,
            'can_add_checkins': False,
            'can_change_checkins': False,
            'can_view_housekeeping': False,
            'can_add_housekeeping': False,
            'can_change_housekeeping': False,
            'can_delete_housekeeping': False,
            'can_view_pos': False,
            'can_add_pos': False,
            'can_change_pos': False,
            'can_delete_pos': False,
        },
        
        'Accountant': {
            # CRUD on Payments
            'can_view_payments': True,
            'can_add_payments': True,
            'can_change_payments': True,
            'can_delete_payments': True,
            # CRUD on Billing
            'can_view_billing': True,
            'can_add_billing': True,
            'can_change_billing': True,
            'can_delete_billing': True,
            # View all Reports (Financial focus)
            'can_view_reports': True,
            # View Reservations (financial data only)
            'can_view_reservations': True,
            'can_add_reservations': False,
            'can_change_reservations': False,
            'can_delete_reservations': False,
            # View POS transactions
            'can_view_pos': True,
            'can_add_pos': False,
            'can_change_pos': False,
            'can_delete_pos': False,
            # Restricted areas
            'can_view_hotels': False,
            'can_change_hotels': False,
            'can_view_rooms': False,
            'can_add_rooms': False,
            'can_change_rooms': False,
            'can_delete_rooms': False,
            'can_view_guests': False,
            'can_add_guests': False,
            'can_change_guests': False,
            'can_delete_guests': False,
            'can_view_staff': False,
            'can_add_staff': False,
            'can_change_staff': False,
            'can_delete_staff': False,
            'can_view_configurations': False,
            'can_add_configurations': False,
            'can_change_configurations': False,
            'can_delete_configurations': False,
            'can_view_companies': False,
            'can_add_companies': False,
            'can_change_companies': False,
            'can_delete_companies': False,
            'can_view_checkins': False,
            'can_add_checkins': False,
            'can_change_checkins': False,
            'can_view_housekeeping': False,
            'can_add_housekeeping': False,
            'can_change_housekeeping': False,
            'can_delete_housekeeping': False,
            'can_view_maintenance': False,
            'can_add_maintenance': False,
            'can_change_maintenance': False,
            'can_delete_maintenance': False,
            'can_view_inventory': False,
            'can_add_inventory': False,
            'can_change_inventory': False,
            'can_delete_inventory': False,
        },
        
        'Staff': {
            # View assigned schedules
            'can_view_staff': True,  # Own schedule
            'can_add_staff': False,
            'can_change_staff': False,
            'can_delete_staff': False,
            # View basic hotel info
            'can_view_hotels': True,
            'can_change_hotels': False,
            # Submit requests/leave
            'can_view_reports': True,  # Own reports
            # Restricted areas - most management modules
            'can_view_rooms': False,
            'can_add_rooms': False,
            'can_change_rooms': False,
            'can_delete_rooms': False,
            'can_view_reservations': False,
            'can_add_reservations': False,
            'can_change_reservations': False,
            'can_delete_reservations': False,
            'can_view_guests': False,
            'can_add_guests': False,
            'can_change_guests': False,
            'can_delete_guests': False,
            'can_view_billing': False,
            'can_add_billing': False,
            'can_change_billing': False,
            'can_view_payments': False,
            'can_add_payments': False,
            'can_view_configurations': False,
            'can_add_configurations': False,
            'can_change_configurations': False,
            'can_delete_configurations': False,
            'can_view_companies': False,
            'can_add_companies': False,
            'can_change_companies': False,
            'can_delete_companies': False,
            'can_view_checkins': False,
            'can_add_checkins': False,
            'can_change_checkins': False,
            'can_view_housekeeping': False,
            'can_add_housekeeping': False,
            'can_change_housekeeping': False,
            'can_delete_housekeeping': False,
            'can_view_maintenance': False,
            'can_add_maintenance': False,
            'can_change_maintenance': False,
            'can_delete_maintenance': False,
            'can_view_pos': False,
            'can_add_pos': False,
            'can_change_pos': False,
            'can_delete_pos': False,
            'can_view_inventory': False,
            'can_add_inventory': False,
            'can_change_inventory': False,
            'can_delete_inventory': False,
        }
    }
    
    @classmethod
    def apply_role_permissions(cls, user):
        """Apply permissions based on user role"""
        if user.role in cls.ROLE_PERMISSIONS:
            permissions = cls.ROLE_PERMISSIONS[user.role]
            for permission, value in permissions.items():
                setattr(user, permission, value)
            user.save()
    
    @classmethod
    def get_role_navbar_items(cls, role):
        """Get navbar items for specific role"""
        navbar_items = {
            'Owner': [
                {'name': 'Dashboard', 'icon': 'fas fa-tachometer-alt', 'url': 'accounts:owner_dashboard'},
                {'name': 'Hotels', 'icon': 'fas fa-building', 'url': 'hotels:hotel_list'},
                {'name': 'Rooms', 'icon': 'fas fa-bed', 'url': 'hotels:room_list'},
                {'name': 'Reservations', 'icon': 'fas fa-calendar-check', 'url': 'reservations:list'},
                {'name': 'Guests', 'icon': 'fas fa-users', 'url': 'crm:list'},
                {'name': 'Staff', 'icon': 'fas fa-user-tie', 'url': 'staff:list'},
                {'name': 'Operations', 'icon': 'fas fa-cogs', 'submenu': [
                    {'name': 'Front Desk', 'icon': 'fas fa-concierge-bell', 'url': 'front_desk:dashboard'},
                    {'name': 'Housekeeping', 'icon': 'fas fa-broom', 'url': 'housekeeping:task_list'},
                    {'name': 'Maintenance', 'icon': 'fas fa-tools', 'url': 'maintenance:issue_list'},
                    {'name': 'Inventory', 'icon': 'fas fa-boxes', 'url': 'inventory:dashboard'},
                ]},
                {'name': 'Financial', 'icon': 'fas fa-dollar-sign', 'submenu': [
                    {'name': 'Billing', 'icon': 'fas fa-file-invoice', 'url': 'billing:dashboard'},
                    {'name': 'Payments', 'icon': 'fas fa-credit-card', 'url': 'billing:payment_list'},
                    {'name': 'POS', 'icon': 'fas fa-cash-register', 'url': 'pos:dashboard'},
                    {'name': 'Reports', 'icon': 'fas fa-chart-bar', 'url': 'reporting:dashboard'},
                ]},
                {'name': 'Configuration', 'icon': 'fas fa-cog', 'submenu': [
                    {'name': 'Room Types', 'icon': 'fas fa-bed', 'url': 'configurations:room_type_list'},
                    {'name': 'Amenities', 'icon': 'fas fa-star', 'url': 'configurations:amenity_list'},
                    {'name': 'Companies', 'icon': 'fas fa-building', 'url': 'hotels:company_list'},
                ]},
            ],
            
            'Manager': [
                {'name': 'Dashboard', 'icon': 'fas fa-tachometer-alt', 'url': 'accounts:employee_dashboard'},
                {'name': 'Staff Management', 'icon': 'fas fa-users', 'url': 'staff:list'},
                {'name': 'Reservations', 'icon': 'fas fa-calendar-check', 'url': 'reservations:list'},
                {'name': 'Guest Management', 'icon': 'fas fa-address-book', 'url': 'crm:list'},
                {'name': 'Company Contracts', 'icon': 'fas fa-handshake', 'url': 'hotels:company_list'},
                {'name': 'Rooms', 'icon': 'fas fa-bed', 'url': 'hotels:room_list'},
                {'name': 'Reports', 'icon': 'fas fa-chart-line', 'url': 'reporting:dashboard'},
                {'name': 'Payments', 'icon': 'fas fa-credit-card', 'url': 'billing:payment_list'},
                {'name': 'Daily Operations', 'icon': 'fas fa-tasks', 'submenu': [
                    {'name': 'Housekeeping', 'icon': 'fas fa-broom', 'url': 'housekeeping:task_list'},
                    {'name': 'Maintenance', 'icon': 'fas fa-tools', 'url': 'maintenance:issue_list'},
                    {'name': 'Inventory', 'icon': 'fas fa-boxes', 'url': 'inventory:dashboard'},
                ]},
            ],
            
            'Receptionist': [
                {'name': 'Dashboard', 'icon': 'fas fa-tachometer-alt', 'url': 'accounts:employee_dashboard'},
                {'name': 'Reservations', 'icon': 'fas fa-calendar-check', 'url': 'reservations:list'},
                {'name': 'Guest Management', 'icon': 'fas fa-users', 'url': 'crm:list'},
                {'name': 'Check-in/Check-out', 'icon': 'fas fa-door-open', 'url': 'front_desk:dashboard'},
                {'name': 'Room Availability', 'icon': 'fas fa-bed', 'url': 'hotels:room_list'},
                {'name': 'Payments', 'icon': 'fas fa-credit-card', 'url': 'billing:payment_list'},
                {'name': 'Billing', 'icon': 'fas fa-file-invoice', 'url': 'billing:dashboard'},
                {'name': "Today's Report", 'icon': 'fas fa-chart-bar', 'url': 'reporting:dashboard'},
            ],
            
            'Housekeeping': [
                {'name': 'Dashboard', 'icon': 'fas fa-tachometer-alt', 'url': 'accounts:employee_dashboard'},
                {'name': 'Room Status', 'icon': 'fas fa-bed', 'url': 'hotels:room_list'},
                {'name': 'Cleaning Schedule', 'icon': 'fas fa-calendar', 'url': 'housekeeping:task_list'},
                {'name': 'Task Assignment', 'icon': 'fas fa-tasks', 'url': 'housekeeping:task_list'},
                {'name': 'Maintenance Requests', 'icon': 'fas fa-tools', 'url': 'maintenance:issue_list'},
                {'name': "Today's Tasks", 'icon': 'fas fa-list-check', 'url': 'housekeeping:task_list'},
            ],
            
            'Maintenance': [
                {'name': 'Dashboard', 'icon': 'fas fa-tachometer-alt', 'url': 'accounts:employee_dashboard'},
                {'name': 'Active Requests', 'icon': 'fas fa-exclamation-triangle', 'url': 'maintenance:issue_list'},
                {'name': 'Completed Tasks', 'icon': 'fas fa-check-circle', 'url': 'maintenance:issue_list'},
                {'name': 'Inventory', 'icon': 'fas fa-boxes', 'url': 'inventory:dashboard'},
                {'name': 'Equipment Status', 'icon': 'fas fa-cogs', 'url': 'maintenance:issue_list'},
                {'name': 'Reports', 'icon': 'fas fa-chart-bar', 'url': 'reporting:dashboard'},
            ],
            
            'Accountant': [
                {'name': 'Dashboard', 'icon': 'fas fa-tachometer-alt', 'url': 'accounts:employee_dashboard'},
                {'name': 'Payments', 'icon': 'fas fa-credit-card', 'url': 'billing:payment_list'},
                {'name': 'Billing', 'icon': 'fas fa-file-invoice', 'url': 'billing:dashboard'},
                {'name': 'Financial Reports', 'icon': 'fas fa-chart-line', 'url': 'reporting:dashboard'},
                {'name': 'POS Transactions', 'icon': 'fas fa-cash-register', 'url': 'pos:dashboard'},
                {'name': 'Tax Records', 'icon': 'fas fa-file-alt', 'url': 'billing:dashboard'},
                {'name': 'Export Data', 'icon': 'fas fa-download', 'url': 'reporting:dashboard'},
            ],
            
            'Staff': [
                {'name': 'Dashboard', 'icon': 'fas fa-tachometer-alt', 'url': 'accounts:employee_dashboard'},
                {'name': 'My Schedule', 'icon': 'fas fa-calendar', 'url': 'staff:schedule'},
                {'name': 'Task Status', 'icon': 'fas fa-tasks', 'url': 'staff:performance'},
                {'name': 'Hotel Info', 'icon': 'fas fa-info-circle', 'url': 'hotels:hotel_list'},
                {'name': 'Submit Request', 'icon': 'fas fa-paper-plane', 'url': 'staff:send_message'},
            ]
        }
        
        return navbar_items.get(role, [])
    
    @classmethod
    def get_role_dashboard_widgets(cls, role):
        """Get dashboard widgets for specific role"""
        dashboard_widgets = {
            'Receptionist': [
                {'title': "Today's Check-ins", 'icon': 'fas fa-sign-in-alt', 'color': 'blue'},
                {'title': "Today's Check-outs", 'icon': 'fas fa-sign-out-alt', 'color': 'green'},
                {'title': 'Room Availability', 'icon': 'fas fa-bed', 'color': 'purple'},
                {'title': 'Pending Payments', 'icon': 'fas fa-credit-card', 'color': 'yellow'},
                {'title': 'Recent Arrivals', 'icon': 'fas fa-users', 'color': 'indigo'},
            ],
            
            'Manager': [
                {'title': 'Department Performance', 'icon': 'fas fa-chart-line', 'color': 'blue'},
                {'title': 'Staff Attendance', 'icon': 'fas fa-user-check', 'color': 'green'},
                {'title': 'Occupancy Statistics', 'icon': 'fas fa-percentage', 'color': 'purple'},
                {'title': 'Pending Approvals', 'icon': 'fas fa-clipboard-check', 'color': 'yellow'},
                {'title': 'Revenue Summary', 'icon': 'fas fa-dollar-sign', 'color': 'indigo'},
            ],
            
            'Housekeeping': [
                {'title': 'Room Status by Floor', 'icon': 'fas fa-building', 'color': 'blue'},
                {'title': "Today's Cleaning Schedule", 'icon': 'fas fa-calendar-day', 'color': 'green'},
                {'title': 'Completed/Pending Tasks', 'icon': 'fas fa-tasks', 'color': 'purple'},
                {'title': 'Maintenance Requests', 'icon': 'fas fa-tools', 'color': 'yellow'},
                {'title': 'Supply Status', 'icon': 'fas fa-boxes', 'color': 'indigo'},
            ],
            
            'Maintenance': [
                {'title': 'Active/Pending Requests', 'icon': 'fas fa-exclamation-circle', 'color': 'red'},
                {'title': 'Priority Tasks', 'icon': 'fas fa-star', 'color': 'yellow'},
                {'title': 'Inventory Alerts', 'icon': 'fas fa-bell', 'color': 'orange'},
                {'title': 'Completed Jobs This Week', 'icon': 'fas fa-check-circle', 'color': 'green'},
            ],
            
            'Accountant': [
                {'title': 'Daily/Weekly/Monthly Revenue', 'icon': 'fas fa-chart-bar', 'color': 'green'},
                {'title': 'Outstanding Payments', 'icon': 'fas fa-exclamation-triangle', 'color': 'yellow'},
                {'title': 'Tax Summary', 'icon': 'fas fa-file-alt', 'color': 'blue'},
                {'title': 'Payment Collection Chart', 'icon': 'fas fa-chart-pie', 'color': 'purple'},
                {'title': 'Financial KPIs', 'icon': 'fas fa-tachometer-alt', 'color': 'indigo'},
            ]
        }
        
        return dashboard_widgets.get(role, [])