from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from hotels.models import Hotel
from configurations.models import RoomType, BedType, Floor, Amenity

User = get_user_model()

class ConfigurationPermissionTestCase(TestCase):
    """Test cases specifically for configuration permissions"""
    
    def setUp(self):
        """Set up test data for configuration permission tests"""
        self.client = Client()
        
        # Create hotel owner
        self.owner = User.objects.create_user(
            username='config_owner',
            email='config_owner@test.com',
            password='testpass123',
            role='Owner'
        )
        
        # Create hotel
        self.hotel = Hotel.objects.create(
            name='Config Test Hotel',
            address='Config Test St',
            city='Test City',
            country='Test Country',
            owner=self.owner
        )
        
        # Create staff with different configuration permissions
        self.staff_view_only = User.objects.create_user(
            username='config_view_only',
            email='config_view@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_configurations=True
        )
        
        self.staff_can_add = User.objects.create_user(
            username='config_can_add',
            email='config_add@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_configurations=True,
            can_add_configurations=True
        )
        
        self.staff_can_edit = User.objects.create_user(
            username='config_can_edit',
            email='config_edit@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_configurations=True,
            can_change_configurations=True
        )
        
        self.staff_can_delete = User.objects.create_user(
            username='config_can_delete',
            email='config_delete@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_configurations=True,
            can_delete_configurations=True
        )
        
        self.staff_full_access = User.objects.create_user(
            username='config_full_access',
            email='config_full@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_configurations=True,
            can_add_configurations=True,
            can_change_configurations=True,
            can_delete_configurations=True
        )
        
        self.staff_no_access = User.objects.create_user(
            username='config_no_access',
            email='config_no@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel
        )
        
        # Create test configuration objects
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            name='Test Room Type'
        )
        
        self.bed_type = BedType.objects.create(
            hotel=self.hotel,
            name='Test Bed Type'
        )
        
        self.floor = Floor.objects.create(
            hotel=self.hotel,
            name='Test Floor',
            number=1
        )
        
        self.amenity = Amenity.objects.create(
            hotel=self.hotel,
            name='Test Amenity'
        )

    def test_room_type_view_permission(self):
        """Test room type view permission"""
        
        # Staff with view permission can access list
        self.client.login(username='config_view_only', password='testpass123')
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)
        
        # Staff without view permission cannot access list
        self.client.login(username='config_no_access', password='testpass123')
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 302)

    def test_room_type_add_permission(self):
        """Test room type add permission"""
        
        # Staff with add permission can access create form
        self.client.login(username='config_can_add', password='testpass123')
        response = self.client.get(reverse('configurations:room_type_create'))
        self.assertEqual(response.status_code, 200)
        
        # Staff with add permission can create room type
        response = self.client.post(reverse('configurations:room_type_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'New Room Type',
            'description': 'New room type description'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify room type was created
        self.assertTrue(RoomType.objects.filter(name='New Room Type').exists())
        
        # Staff without add permission cannot access create form
        self.client.login(username='config_view_only', password='testpass123')
        response = self.client.get(reverse('configurations:room_type_create'))
        self.assertEqual(response.status_code, 302)

    def test_room_type_edit_permission(self):
        """Test room type edit permission"""
        
        # Staff with edit permission can access edit form
        self.client.login(username='config_can_edit', password='testpass123')
        response = self.client.get(reverse('configurations:room_type_edit', args=[self.room_type.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Staff with edit permission can update room type
        response = self.client.post(reverse('configurations:room_type_edit', args=[self.room_type.pk]), {
            'name': 'Updated Room Type',
            'description': 'Updated description'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify room type was updated
        self.room_type.refresh_from_db()
        self.assertEqual(self.room_type.name, 'Updated Room Type')
        
        # Staff without edit permission cannot access edit form
        self.client.login(username='config_view_only', password='testpass123')
        response = self.client.get(reverse('configurations:room_type_edit', args=[self.room_type.pk]))
        self.assertEqual(response.status_code, 302)

    def test_room_type_delete_permission(self):
        """Test room type delete permission"""
        
        # Create a room type to delete
        room_type_to_delete = RoomType.objects.create(
            hotel=self.hotel,
            name='Room Type to Delete'
        )
        
        # Staff with delete permission can delete room type
        self.client.login(username='config_can_delete', password='testpass123')
        response = self.client.post(reverse('configurations:room_type_delete', args=[room_type_to_delete.pk]))
        self.assertEqual(response.status_code, 302)
        
        # Verify room type was deleted
        self.assertFalse(RoomType.objects.filter(pk=room_type_to_delete.pk).exists())
        
        # Staff without delete permission cannot delete room type
        room_type_to_delete2 = RoomType.objects.create(
            hotel=self.hotel,
            name='Room Type to Delete 2'
        )
        
        self.client.login(username='config_view_only', password='testpass123')
        response = self.client.post(reverse('configurations:room_type_delete', args=[room_type_to_delete2.pk]))
        self.assertEqual(response.status_code, 302)

    def test_bed_type_permissions(self):
        """Test bed type permissions"""
        
        # Test view permission
        self.client.login(username='config_view_only', password='testpass123')
        response = self.client.get(reverse('configurations:bed_type_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test add permission
        self.client.login(username='config_can_add', password='testpass123')
        response = self.client.post(reverse('configurations:bed_type_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'New Bed Type',
            'description': 'New bed type description'
        })
        self.assertEqual(response.status_code, 302)
        
        # Test edit permission
        self.client.login(username='config_can_edit', password='testpass123')
        response = self.client.post(reverse('configurations:bed_type_edit', args=[self.bed_type.pk]), {
            'name': 'Updated Bed Type',
            'description': 'Updated description'
        })
        self.assertEqual(response.status_code, 302)

    def test_floor_permissions(self):
        """Test floor permissions"""
        
        # Test view permission
        self.client.login(username='config_view_only', password='testpass123')
        response = self.client.get(reverse('configurations:floor_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test add permission
        self.client.login(username='config_can_add', password='testpass123')
        response = self.client.post(reverse('configurations:floor_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'New Floor',
            'number': 2,
            'description': 'New floor description'
        })
        self.assertEqual(response.status_code, 302)
        
        # Test edit permission
        self.client.login(username='config_can_edit', password='testpass123')
        response = self.client.post(reverse('configurations:floor_edit', args=[self.floor.pk]), {
            'name': 'Updated Floor',
            'number': 1,
            'description': 'Updated description'
        })
        self.assertEqual(response.status_code, 302)

    def test_amenity_permissions(self):
        """Test amenity permissions"""
        
        # Test view permission
        self.client.login(username='config_view_only', password='testpass123')
        response = self.client.get(reverse('configurations:amenity_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test add permission
        self.client.login(username='config_can_add', password='testpass123')
        response = self.client.post(reverse('configurations:amenity_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'New Amenity',
            'description': 'New amenity description',
            'icon': 'fas fa-wifi'
        })
        self.assertEqual(response.status_code, 302)
        
        # Test edit permission
        self.client.login(username='config_can_edit', password='testpass123')
        response = self.client.post(reverse('configurations:amenity_edit', args=[self.amenity.pk]), {
            'name': 'Updated Amenity',
            'description': 'Updated description',
            'icon': 'fas fa-pool'
        })
        self.assertEqual(response.status_code, 302)

    def test_owner_has_all_configuration_permissions(self):
        """Test that hotel owner has all configuration permissions"""
        
        self.client.login(username='config_owner', password='testpass123')
        
        # Owner can view all configuration lists
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:bed_type_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:floor_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('configurations:amenity_list'))
        self.assertEqual(response.status_code, 200)
        
        # Owner can create configurations
        response = self.client.post(reverse('configurations:room_type_create'), {
            'hotel': self.hotel.hotel_id,
            'name': 'Owner Room Type',
            'description': 'Created by owner'
        })
        self.assertEqual(response.status_code, 302)
        
        # Owner can edit configurations
        response = self.client.post(reverse('configurations:room_type_edit', args=[self.room_type.pk]), {
            'name': 'Owner Updated Room Type',
            'description': 'Updated by owner'
        })
        self.assertEqual(response.status_code, 302)
        
        # Owner can delete configurations
        room_type_to_delete = RoomType.objects.create(
            hotel=self.hotel,
            name='Owner Delete Test'
        )
        
        response = self.client.post(reverse('configurations:room_type_delete', args=[room_type_to_delete.pk]))
        self.assertEqual(response.status_code, 302)

    def test_hotel_isolation_in_configurations(self):
        """Test that staff can only access configurations from their assigned hotel"""
        
        # Create another hotel and owner
        other_owner = User.objects.create_user(
            username='other_config_owner',
            email='other_config_owner@test.com',
            password='testpass123',
            role='Owner'
        )
        
        other_hotel = Hotel.objects.create(
            name='Other Config Hotel',
            address='Other Config St',
            city='Other City',
            country='Other Country',
            owner=other_owner
        )
        
        other_room_type = RoomType.objects.create(
            hotel=other_hotel,
            name='Other Hotel Room Type'
        )
        
        # Staff from first hotel should not be able to edit other hotel's configurations
        self.client.login(username='config_full_access', password='testpass123')
        
        # Should be redirected when trying to edit other hotel's room type
        response = self.client.get(reverse('configurations:room_type_edit', args=[other_room_type.pk]))
        self.assertEqual(response.status_code, 302)
        
        # Should be redirected when trying to delete other hotel's room type
        response = self.client.post(reverse('configurations:room_type_delete', args=[other_room_type.pk]))
        self.assertEqual(response.status_code, 302)

    def test_configuration_permissions_with_no_assigned_hotel(self):
        """Test configuration permissions for staff with no assigned hotel"""
        
        # Create staff with no assigned hotel
        staff_no_hotel = User.objects.create_user(
            username='staff_no_hotel',
            email='staff_no_hotel@test.com',
            password='testpass123',
            role='Staff',
            can_view_configurations=True,
            can_add_configurations=True,
            can_change_configurations=True,
            can_delete_configurations=True
        )
        
        self.client.login(username='staff_no_hotel', password='testpass123')
        
        # Staff with no assigned hotel should see empty lists
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)
        
        # Should not be able to create configurations without hotel assignment
        response = self.client.get(reverse('configurations:room_type_create'))
        self.assertEqual(response.status_code, 200)  # Can access form but hotel list will be empty

    def tearDown(self):
        """Clean up test data"""
        User.objects.all().delete()
        Hotel.objects.all().delete()
        RoomType.objects.all().delete()
        BedType.objects.all().delete()
        Floor.objects.all().delete()
        Amenity.objects.all().delete()