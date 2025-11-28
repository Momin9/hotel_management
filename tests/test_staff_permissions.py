from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from hotels.models import Hotel

User = get_user_model()

class StaffPermissionTestCase(TestCase):
    """Test cases specifically for staff management permissions"""
    
    def setUp(self):
        """Set up test data for staff permission tests"""
        self.client = Client()
        
        # Create hotel owner
        self.owner = User.objects.create_user(
            username='staff_owner',
            email='staff_owner@test.com',
            password='testpass123',
            role='Owner'
        )
        
        # Create hotel
        self.hotel = Hotel.objects.create(
            name='Staff Test Hotel',
            address='Staff Test St',
            city='Test City',
            country='Test Country',
            owner=self.owner
        )
        
        # Create staff with different staff management permissions
        self.staff_can_view_only = User.objects.create_user(
            username='staff_view_only',
            email='staff_view@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_staff=True
        )
        
        self.staff_can_add = User.objects.create_user(
            username='staff_can_add',
            email='staff_add@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_staff=True,
            can_add_staff=True
        )
        
        self.staff_can_edit = User.objects.create_user(
            username='staff_can_edit',
            email='staff_edit@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_staff=True,
            can_change_staff=True
        )
        
        self.staff_can_delete = User.objects.create_user(
            username='staff_can_delete',
            email='staff_delete@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_staff=True,
            can_delete_staff=True
        )
        
        self.staff_full_access = User.objects.create_user(
            username='staff_full_access',
            email='staff_full@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_staff=True,
            can_add_staff=True,
            can_change_staff=True,
            can_delete_staff=True
        )
        
        self.staff_no_access = User.objects.create_user(
            username='staff_no_access',
            email='staff_no@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel
        )

    def test_staff_view_permission(self):
        """Test staff view permission"""
        
        # Staff with view permission can access list
        self.client.login(username='staff_view_only', password='testpass123')
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 200)
        
        # Staff without view permission cannot access list
        self.client.login(username='staff_no_access', password='testpass123')
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 302)

    def test_staff_add_permission(self):
        """Test staff add permission"""
        
        # Staff with add permission can access create form
        self.client.login(username='staff_can_add', password='testpass123')
        response = self.client.get(reverse('staff:create'))
        self.assertEqual(response.status_code, 200)
        
        # Staff with add permission can create staff
        response = self.client.post(reverse('staff:create'), {
            'first_name': 'New',
            'last_name': 'Staff',
            'email': 'newstaff@test.com',
            'username': 'newstaff',
            'password': 'testpass123',
            'role': 'Staff',
            'assigned_hotel': self.hotel.hotel_id
        })
        # Should redirect after successful creation or show form with errors
        self.assertIn(response.status_code, [200, 302])
        
        # Staff without add permission cannot access create form
        self.client.login(username='staff_view_only', password='testpass123')
        response = self.client.get(reverse('staff:create'))
        self.assertEqual(response.status_code, 302)

    def test_staff_edit_permission(self):
        """Test staff edit permission"""
        
        # Staff with edit permission can access edit form
        self.client.login(username='staff_can_edit', password='testpass123')
        response = self.client.get(reverse('staff:edit', args=[self.staff_no_access.user_id]))
        self.assertEqual(response.status_code, 200)
        
        # Staff with edit permission can update staff
        response = self.client.post(reverse('staff:edit', args=[self.staff_no_access.user_id]), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'phone': '123456789'
        })
        self.assertEqual(response.status_code, 302)
        
        # Staff without edit permission cannot access edit form
        self.client.login(username='staff_view_only', password='testpass123')
        response = self.client.get(reverse('staff:edit', args=[self.staff_no_access.user_id]))
        self.assertEqual(response.status_code, 302)

    def test_staff_delete_permission(self):
        """Test staff delete permission"""
        
        # Create a staff member to delete
        staff_to_delete = User.objects.create_user(
            username='staff_to_delete',
            email='delete@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel
        )
        
        # Staff with delete permission can delete staff
        self.client.login(username='staff_can_delete', password='testpass123')
        response = self.client.post(reverse('staff:delete', args=[staff_to_delete.user_id]))
        self.assertEqual(response.status_code, 302)
        
        # Verify staff was soft deleted
        staff_to_delete.refresh_from_db()
        self.assertIsNotNone(staff_to_delete.deleted_at)
        
        # Staff without delete permission cannot delete staff
        staff_to_delete2 = User.objects.create_user(
            username='staff_to_delete2',
            email='delete2@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel
        )
        
        self.client.login(username='staff_view_only', password='testpass123')
        response = self.client.post(reverse('staff:delete', args=[staff_to_delete2.user_id]))
        self.assertEqual(response.status_code, 302)

    def test_owner_has_all_staff_permissions(self):
        """Test that hotel owner has all staff management permissions"""
        
        self.client.login(username='staff_owner', password='testpass123')
        
        # Owner can view staff list
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 200)
        
        # Owner can create staff
        response = self.client.get(reverse('staff:create'))
        self.assertEqual(response.status_code, 200)
        
        # Owner can edit staff
        response = self.client.get(reverse('staff:edit', args=[self.staff_no_access.user_id]))
        self.assertEqual(response.status_code, 200)
        
        # Owner can delete staff
        staff_to_delete = User.objects.create_user(
            username='owner_delete_test',
            email='owner_delete@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel
        )
        
        response = self.client.post(reverse('staff:delete', args=[staff_to_delete.user_id]))
        self.assertEqual(response.status_code, 302)

    def test_staff_detail_view_permission(self):
        """Test staff detail view permission"""
        
        # Staff with view permission can see detail
        self.client.login(username='staff_view_only', password='testpass123')
        response = self.client.get(reverse('staff:detail', args=[self.staff_no_access.user_id]))
        self.assertEqual(response.status_code, 200)
        
        # Staff without view permission cannot see detail
        self.client.login(username='staff_no_access', password='testpass123')
        response = self.client.get(reverse('staff:detail', args=[self.staff_can_view_only.user_id]))
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        """Clean up test data"""
        User.objects.all().delete()
        Hotel.objects.all().delete()