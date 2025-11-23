from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.roles import RoleManager

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up roles and create demo users'

    def handle(self, *args, **options):
        # Create roles and permissions
        RoleManager.create_roles_and_permissions()
        self.stdout.write(self.style.SUCCESS('Roles and permissions created successfully!'))

        # Update existing admin1 user
        try:
            admin_user = User.objects.get(email='admin@demo.com')
            RoleManager.assign_role_to_user(admin_user, 'SUPER_ADMIN')
            self.stdout.write(self.style.SUCCESS('admin1 assigned Super Admin role'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('admin1 user not found'))

        # Create demo users
        users_to_create = [
            {
                'email': 'owner@demo.com',
                'password': 'owner123',
                'first_name': 'Hotel',
                'last_name': 'Owner',
                'role': 'HOTEL_OWNER'
            },
            {
                'email': 'manager@demo.com', 
                'password': 'manager123',
                'first_name': 'Hotel',
                'last_name': 'Manager',
                'role': 'HOTEL_MANAGER'
            },
            {
                'email': 'frontdesk@demo.com',
                'password': 'front123',
                'first_name': 'Front',
                'last_name': 'Desk',
                'role': 'FRONT_DESK'
            },
            {
                'email': 'housekeeper@demo.com',
                'password': 'house123',
                'first_name': 'House',
                'last_name': 'Keeper',
                'role': 'HOUSEKEEPING'
            },
            {
                'email': 'maintenance@demo.com',
                'password': 'maint123',
                'first_name': 'Maintenance',
                'last_name': 'Staff',
                'role': 'MAINTENANCE'
            },
            {
                'email': 'kitchen@demo.com',
                'password': 'kitchen123',
                'first_name': 'Kitchen',
                'last_name': 'Staff',
                'role': 'KITCHEN_STAFF'
            },
            {
                'email': 'accountant@demo.com',
                'password': 'account123',
                'first_name': 'Account',
                'last_name': 'Manager',
                'role': 'ACCOUNTANT'
            }
        ]

        for user_data in users_to_create:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f"Created user: {user_data['email']}")
            else:
                self.stdout.write(f"User already exists: {user_data['email']}")
            
            # Assign role
            RoleManager.assign_role_to_user(user, user_data['role'])
            self.stdout.write(f"Assigned {user_data['role']} role to {user_data['email']}")

        self.stdout.write(self.style.SUCCESS('\nDemo users created:'))
        self.stdout.write('Super Admin: admin1 / admin (Django admin access)')
        self.stdout.write('Hotel Owner: owner@demo.com / owner123')
        self.stdout.write('Hotel Manager: manager@demo.com / manager123')
        self.stdout.write('Front Desk: frontdesk@demo.com / front123')
        self.stdout.write('Housekeeper: housekeeper@demo.com / house123')
        self.stdout.write('Maintenance: maintenance@demo.com / maint123')
        self.stdout.write('Kitchen Staff: kitchen@demo.com / kitchen123')
        self.stdout.write('Accountant: accountant@demo.com / account123')
        self.stdout.write(self.style.SUCCESS('\nRole setup completed!'))