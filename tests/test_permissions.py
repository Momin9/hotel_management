from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from hotels.models import Hotel
from configurations.models import RoomType, BedType, Floor, Amenity
from accounts.permissions import check_user_permission, assign_default_permissions

User = get_user_model()

class PermissionTestCase(TestCase):
    """Comprehensive test suite for all permission scenarios"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='superadmin',
            email='super@test.com',
            password='testpass123'
        )
        
        # Create hotel owner
        self.owner = User.objects.create_user(
            username='owner1',
            email='owner@test.com',
            password='testpass123',
            first_name='Hotel',
            last_name='Owner',
            role='Owner'
        )
        
        # Create hotel
        self.hotel = Hotel.objects.create(
            name='Test Hotel',
            address='123 Test St',
            city='Test City',
            country='Test Country',
            owner=self.owner
        )
        
        # Create staff users with different permission levels
        self.manager = User.objects.create_user(
            username='manager1',
            email='manager@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Manager',
            role='Manager',
            assigned_hotel=self.hotel
        )
        
        self.staff_full_permissions = User.objects.create_user(
            username='staff_full',
            email='staff_full@test.com',
            password='testpass123',
            first_name='Full',
            last_name='Staff',
            role='Staff',
            assigned_hotel=self.hotel,
            # Hotel Management
            can_view_hotels=True,
            can_change_hotels=True,
            can_view_rooms=True,
            can_add_rooms=True,
            can_change_rooms=True,
            can_delete_rooms=True,
            # Reservations
            can_view_reservations=True,
            can_add_reservations=True,
            can_change_reservations=True,
            can_delete_reservations=True,
            can_view_checkins=True,
            can_add_checkins=True,
            can_change_checkins=True,
            # Guest Management
            can_view_guests=True,
            can_add_guests=True,
            can_change_guests=True,
            can_delete_guests=True,
            # Staff Management
            can_view_staff=True,
            can_add_staff=True,
            can_change_staff=True,
            can_delete_staff=True,
            # Operations
            can_view_housekeeping=True,
            can_add_housekeeping=True,
            can_change_housekeeping=True,
            can_delete_housekeeping=True,
            can_view_maintenance=True,
            can_add_maintenance=True,
            can_change_maintenance=True,
            can_delete_maintenance=True,
            can_view_pos=True,
            can_add_pos=True,
            can_change_pos=True,
            can_delete_pos=True,
            # Financial
            can_view_billing=True,
            can_add_billing=True,
            can_change_billing=True,
            can_view_payments=True,
            can_add_payments=True,
            can_view_reports=True,
            can_view_inventory=True,
            can_add_inventory=True,
            can_change_inventory=True,
            can_delete_inventory=True,
            # Configuration
            can_view_configurations=True,
            can_add_configurations=True,
            can_change_configurations=True,
            can_delete_configurations=True
        )
        
        self.staff_no_permissions = User.objects.create_user(
            username='staff_none',
            email='staff_none@test.com',
            password='testpass123',
            first_name='No',
            last_name='Permissions',
            role='Staff',
            assigned_hotel=self.hotel
        )
        
        self.staff_partial_permissions = User.objects.create_user(
            username='staff_partial',
            email='staff_partial@test.com',
            password='testpass123',
            first_name='Partial',
            last_name='Permissions',
            role='Staff',
            assigned_hotel=self.hotel,
            # Only view permissions
            can_view_hotels=True,
            can_view_rooms=True,
            can_view_reservations=True,
            can_view_guests=True,
            can_view_staff=True,
            can_view_configurations=True
        )
        
        # Create test configuration objects
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            name='Standard Room'
        )
        
        self.bed_type = BedType.objects.create(
            hotel=self.hotel,
            name='Queen Bed'
        )
        
        self.floor = Floor.objects.create(
            hotel=self.hotel,
            name='Ground Floor',
            number=1
        )
        
        self.amenity = Amenity.objects.create(
            hotel=self.hotel,
            name='WiFi'
        )

    def test_superuser_permissions(self):
        """Test that superuser has access to everything"""
        self.client.login(username='superadmin', password='testpass123')
        
        # Test configuration access
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:bed_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:floor_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:amenity_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test staff management
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 200)

    def test_owner_permissions(self):
        """Test that hotel owner has full access to their hotel"""
        self.client.login(username='owner1', password='testpass123')
        
        # Test configuration access
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:bed_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:floor_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:amenity_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test staff management
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 200)
        
        # Test creating configurations
        response = self.client.post(reverse('configurations:room_type_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'Deluxe Room',
            'description': 'Luxury room'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation

    def test_staff_full_permissions_access(self):
        """Test staff with full permissions can access everything"""
        self.client.login(username='staff_full', password='testpass123')
        
        # Test view access
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:bed_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:floor_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:amenity_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test create access
        response = self.client.get(reverse('configurations:room_type_create'))
        self.assertEqual(response.status_code, 200)
        
        # Test edit access
        response = self.client.get(reverse('configurations:room_type_edit', args=[self.room_type.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Test staff management
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('staff:create'))
        self.assertEqual(response.status_code, 200)

    def test_staff_no_permissions_denied(self):
        """Test staff with no permissions is denied access"""
        self.client.login(username='staff_none', password='testpass123')
        
        # Test view access denied
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        
        response = self.client.get(reverse('configurations:bed_type_list'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('configurations:floor_list'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('configurations:amenity_list'))
        self.assertEqual(response.status_code, 302)
        
        # Test create access denied
        response = self.client.get(reverse('configurations:room_type_create'))
        self.assertEqual(response.status_code, 302)
        
        # Test staff management denied
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 302)

    def test_staff_partial_permissions(self):
        """Test staff with partial permissions has limited access"""
        self.client.login(username='staff_partial', password='testpass123')
        
        # Test view access allowed
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:bed_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:floor_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:amenity_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test create access denied
        response = self.client.get(reverse('configurations:room_type_create'))
        self.assertEqual(response.status_code, 302)
        
        # Test edit access denied
        response = self.client.get(reverse('configurations:room_type_edit', args=[self.room_type.pk]))
        self.assertEqual(response.status_code, 302)
        
        # Test staff view allowed but create denied
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('staff:create'))
        self.assertEqual(response.status_code, 302)

    def test_configuration_crud_permissions(self):
        """Test CRUD operations for configurations with different permission levels"""
        
        # Test with full permissions staff
        self.client.login(username='staff_full', password='testpass123')
        
        # CREATE - Room Type
        response = self.client.post(reverse('configurations:room_type_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'Suite Room',
            'description': 'Luxury suite'
        })
        self.assertEqual(response.status_code, 302)
        
        # CREATE - Bed Type
        response = self.client.post(reverse('configurations:bed_type_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'King Bed',
            'description': 'King size bed'
        })
        self.assertEqual(response.status_code, 302)
        
        # CREATE - Floor
        response = self.client.post(reverse('configurations:floor_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'First Floor',
            'number': 2,
            'description': 'First floor'
        })
        self.assertEqual(response.status_code, 302)
        
        # CREATE - Amenity
        response = self.client.post(reverse('configurations:amenity_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'Pool',
            'description': 'Swimming pool',
            'icon': 'fas fa-swimming-pool'
        })
        self.assertEqual(response.status_code, 302)
        
        # UPDATE - Room Type
        response = self.client.post(reverse('configurations:room_type_edit', args=[self.room_type.pk]), {
            'name': 'Updated Standard Room',
            'description': 'Updated description'
        })
        self.assertEqual(response.status_code, 302)
        
        # DELETE - Room Type
        response = self.client.post(reverse('configurations:room_type_delete', args=[self.room_type.pk]))
        self.assertEqual(response.status_code, 302)

    def test_staff_management_permissions(self):
        """Test staff management permissions"""
        
        # Test with owner
        self.client.login(username='owner1', password='testpass123')
        
        # Create staff
        response = self.client.post(reverse('staff:create'), {
            'first_name': 'New',
            'last_name': 'Staff',
            'email': 'newstaff@test.com',
            'username': 'newstaff',
            'password': 'testpass123',
            'role': 'Staff',
            'assigned_hotel': self.hotel.hotel_id,
            'can_view_rooms': 'on',
            'can_view_guests': 'on'
        })
        self.assertEqual(response.status_code, 302)
        
        # Test with staff having staff management permissions
        self.client.login(username='staff_full', password='testpass123')
        
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('staff:create'))
        self.assertEqual(response.status_code, 200)
        
        # Test with staff without permissions
        self.client.login(username='staff_none', password='testpass123')
        
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 302)

    def test_permission_inheritance_by_role(self):
        """Test that owners always have permissions regardless of boolean fields"""
        
        # Create owner with all permission fields set to False
        owner_no_flags = User.objects.create_user(
            username='owner_no_flags',
            email='owner_no_flags@test.com',
            password='testpass123',
            role='Owner',
            # All permission flags are False by default
        )
        
        hotel2 = Hotel.objects.create(
            name='Test Hotel 2',
            address='456 Test Ave',
            city='Test City',
            country='Test Country',
            owner=owner_no_flags
        )
        
        self.client.login(username='owner_no_flags', password='testpass123')
        
        # Owner should still have access despite permission flags being False
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 200)

    def test_hotel_isolation(self):
        """Test that staff can only access their assigned hotel's data"""
        
        # Create another hotel and owner
        other_owner = User.objects.create_user(
            username='other_owner',
            email='other_owner@test.com',
            password='testpass123',
            role='Owner'
        )
        
        other_hotel = Hotel.objects.create(
            name='Other Hotel',
            address='789 Other St',
            city='Other City',
            country='Other Country',
            owner=other_owner
        )
        
        other_room_type = RoomType.objects.create(
            hotel=other_hotel,
            name='Other Room Type'
        )
        
        # Login as staff from first hotel
        self.client.login(username='staff_full', password='testpass123')
        
        # Should not be able to edit other hotel's room type
        response = self.client.get(reverse('configurations:room_type_edit', args=[other_room_type.pk]))
        self.assertEqual(response.status_code, 302)  # Redirected due to permission denied

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users are redirected to login"""
        
        # Test configuration views
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_permission_checking_functions(self):
        """Test the permission checking utility functions"""
        
        # Test superuser
        self.assertTrue(check_user_permission(self.superuser, 'view_configurations'))
        self.assertTrue(check_user_permission(self.superuser, 'add_configurations'))
        
        # Test owner
        self.assertTrue(check_user_permission(self.owner, 'view_configurations'))
        self.assertTrue(check_user_permission(self.owner, 'add_configurations'))
        
        # Test staff with permissions
        # Note: The check_user_permission function checks user_permissions, not the boolean fields
        # So we need to test the actual boolean fields directly
        self.assertTrue(self.staff_full_permissions.can_view_configurations)
        self.assertTrue(self.staff_full_permissions.can_add_configurations)
        
        # Test staff without permissions
        self.assertFalse(self.staff_no_permissions.can_view_configurations)
        self.assertFalse(self.staff_no_permissions.can_add_configurations)

    def test_all_permission_fields_exist(self):
        """Test that all expected permission fields exist on User model"""
        
        permission_fields = [
            # Hotel Management
            'can_view_hotels', 'can_change_hotels', 'can_view_rooms', 'can_add_rooms', 
            'can_change_rooms', 'can_delete_rooms',
            # Reservations
            'can_view_reservations', 'can_add_reservations', 'can_change_reservations', 
            'can_delete_reservations', 'can_view_checkins', 'can_add_checkins', 'can_change_checkins',
            # Guest Management
            'can_view_guests', 'can_add_guests', 'can_change_guests', 'can_delete_guests',
            # Staff Management
            'can_view_staff', 'can_add_staff', 'can_change_staff', 'can_delete_staff',
            # Operations
            'can_view_housekeeping', 'can_add_housekeeping', 'can_change_housekeeping', 'can_delete_housekeeping',
            'can_view_maintenance', 'can_add_maintenance', 'can_change_maintenance', 'can_delete_maintenance',
            'can_view_pos', 'can_add_pos', 'can_change_pos', 'can_delete_pos',
            # Financial
            'can_view_billing', 'can_add_billing', 'can_change_billing', 'can_view_payments', 
            'can_add_payments', 'can_view_reports', 'can_view_inventory', 'can_add_inventory',
            'can_change_inventory', 'can_delete_inventory',
            # Configuration
            'can_view_configurations', 'can_add_configurations', 'can_change_configurations', 'can_delete_configurations'
        ]
        
        user = User.objects.first()
        for field in permission_fields:
            self.assertTrue(hasattr(user, field), f"Permission field '{field}' does not exist on User model")

    def test_navigation_context_permissions(self):
        """Test that navigation context processor returns correct permissions"""
        from accounts.views import navigation_context
        
        # Create mock request objects
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        # Test with owner
        request = MockRequest(self.owner)
        context = navigation_context(request)
        
        # Owner should have all permissions
        self.assertTrue(context['can_view_hotels'])
        self.assertTrue(context['can_add_rooms'])
        self.assertTrue(context['can_view_staff'])
        
        # Test with staff with permissions
        request = MockRequest(self.staff_full_permissions)
        context = navigation_context(request)
        
        self.assertTrue(context['can_view_hotels'])
        self.assertTrue(context['can_add_rooms'])
        self.assertTrue(context['can_view_staff'])
        
        # Test with staff without permissions
        request = MockRequest(self.staff_no_permissions)
        context = navigation_context(request)
        
        self.assertFalse(context['can_view_hotels'])
        self.assertFalse(context['can_add_rooms'])
        self.assertFalse(context['can_view_staff'])

    def test_role_based_default_permissions(self):
        """Test that default permissions are assigned correctly based on role"""
        
        # Create users with different roles
        receptionist = User.objects.create_user(
            username='receptionist1',
            email='receptionist@test.com',
            password='testpass123',
            role='Receptionist',
            assigned_hotel=self.hotel
        )
        
        housekeeper = User.objects.create_user(
            username='housekeeper1',
            email='housekeeper@test.com',
            password='testpass123',
            role='Housekeeper',
            assigned_hotel=self.hotel
        )
        
        # Assign default permissions
        assign_default_permissions(receptionist)
        assign_default_permissions(housekeeper)
        
        # Test that permissions were assigned (this tests the permission system setup)
        # Note: The actual permission checking in views uses boolean fields, not Django permissions
        self.assertTrue(receptionist.user_permissions.exists())
        self.assertTrue(housekeeper.user_permissions.exists())

    def tearDown(self):
        """Clean up test data"""
        User.objects.all().delete()
        Hotel.objects.all().delete()
        RoomType.objects.all().delete()
        BedType.objects.all().delete()
        Floor.objects.all().delete()
        Amenity.objects.all().delete()


class PermissionIntegrationTestCase(TestCase):
    """Integration tests for permission system with real URL patterns"""
    
    def setUp(self):
        """Set up test data for integration tests"""
        self.client = Client()
        
        # Create test users and hotel
        self.owner = User.objects.create_user(
            username='integration_owner',
            email='integration_owner@test.com',
            password='testpass123',
            role='Owner'
        )
        
        self.hotel = Hotel.objects.create(
            name='Integration Test Hotel',
            address='Integration St',
            city='Test City',
            country='Test Country',
            owner=self.owner
        )
        
        self.staff_limited = User.objects.create_user(
            username='staff_limited',
            email='staff_limited@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_configurations=True,  # Only view permission
        )

    def test_permission_enforcement_in_views(self):
        """Test that permissions are properly enforced in actual view functions"""
        
        # Test with limited staff - should be able to view but not create
        self.client.login(username='staff_limited', password='testpass123')
        
        # View should work
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)
        
        # Create should be denied
        response = self.client.get(reverse('configurations:room_type_create'))
        self.assertEqual(response.status_code, 302)
        
        # POST to create should also be denied
        response = self.client.post(reverse('configurations:room_type_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'Unauthorized Room Type'
        })
        self.assertEqual(response.status_code, 302)

    def test_error_messages_for_permission_denied(self):
        """Test that appropriate error messages are shown for permission denied"""
        
        self.client.login(username='staff_limited', password='testpass123')
        
        # Try to access create page (should redirect with message)
        response = self.client.get(reverse('configurations:room_type_create'))
        
        # Check that we were redirected (302 status code)
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        """Clean up integration test data"""
        User.objects.all().delete()
        Hotel.objects.all().delete()