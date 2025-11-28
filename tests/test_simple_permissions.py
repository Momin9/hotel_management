from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from hotels.models import Hotel
from configurations.models import RoomType

User = get_user_model()

class SimplePermissionTestCase(TestCase):
    """Simple test cases to debug permission issues"""
    
    def setUp(self):
        """Set up minimal test data"""
        self.client = Client()
        
        # Create hotel owner
        self.owner = User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='testpass123',
            role='Owner'
        )
        
        # Create hotel
        self.hotel = Hotel.objects.create(
            name='Test Hotel',
            address='Test Address',
            city='Test City',
            country='Test Country',
            owner=self.owner
        )
        
        # Create staff with view permission
        self.staff_view = User.objects.create_user(
            username='staffview',
            email='staff@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel,
            can_view_configurations=True
        )
        
        # Create staff with no permissions
        self.staff_none = User.objects.create_user(
            username='staffnone',
            email='staffnone@test.com',
            password='testpass123',
            role='Staff',
            assigned_hotel=self.hotel
        )

    def test_owner_can_access_configurations(self):
        """Test that owner can access configuration pages"""
        self.client.login(username='testowner', password='testpass123')
        
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)

    def test_staff_with_permission_can_view(self):
        """Test that staff with view permission can access list"""
        self.client.login(username='staffview', password='testpass123')
        
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 200)

    def test_staff_without_permission_denied(self):
        """Test that staff without permission is denied"""
        self.client.login(username='staffnone', password='testpass123')
        
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 302)  # Should be redirected

    def test_unauthenticated_redirected_to_login(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('configurations:room_type_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_staff_management_permissions(self):
        """Test staff management permissions"""
        # Owner should have access
        self.client.login(username='testowner', password='testpass123')
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 200)
        
        # Staff without permission should be denied
        self.client.login(username='staffnone', password='testpass123')
        response = self.client.get(reverse('staff:list'))
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        """Clean up test data"""
        User.objects.all().delete()
        Hotel.objects.all().delete()