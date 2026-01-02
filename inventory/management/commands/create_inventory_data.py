from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
import random

from inventory.models import (
    InventoryCategory, Supplier, InventoryItem, 
    StockMovement, PurchaseOrder, PurchaseOrderItem
)
from hotels.models import Hotel

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample inventory data for Oceanview Resort & Spa'

    def handle(self, *args, **options):
        self.stdout.write('Creating inventory sample data...')
        
        # Get Oceanview Resort & Spa
        try:
            hotel = Hotel.objects.get(name="Oceanview Resort & Spa")
        except Hotel.DoesNotExist:
            self.stdout.write(self.style.ERROR('Oceanview Resort & Spa not found'))
            return
        
        # Get admin user for created_by fields
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found'))
            return

        # Create categories
        categories_data = [
            {'name': 'Housekeeping Supplies', 'description': 'Cleaning supplies, linens, toiletries'},
            {'name': 'Food & Beverage', 'description': 'Restaurant and bar inventory'},
            {'name': 'Maintenance Supplies', 'description': 'Tools, parts, and maintenance materials'},
            {'name': 'Guest Amenities', 'description': 'Welcome gifts, spa products, room amenities'},
            {'name': 'Office Supplies', 'description': 'Stationery, printing materials, office equipment'},
            {'name': 'Furniture & Fixtures', 'description': 'Room furniture, lobby fixtures, decorative items'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = InventoryCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create suppliers
        suppliers_data = [
            {
                'name': 'CleanPro Supplies Ltd',
                'contact_person': 'Sarah Johnson',
                'email': 'sarah@cleanpro.com',
                'phone': '+1-555-0101',
                'payment_terms': 'Net 30',
                'rating': 5
            },
            {
                'name': 'Fresh Foods Distributors',
                'contact_person': 'Mike Chen',
                'email': 'mike@freshfoods.com',
                'phone': '+1-555-0102',
                'payment_terms': 'Net 15',
                'rating': 4
            },
            {
                'name': 'Hotel Maintenance Co',
                'contact_person': 'David Wilson',
                'email': 'david@hotelmaint.com',
                'phone': '+1-555-0103',
                'payment_terms': 'Net 30',
                'rating': 5
            },
            {
                'name': 'Luxury Amenities Inc',
                'contact_person': 'Emma Davis',
                'email': 'emma@luxuryamenities.com',
                'phone': '+1-555-0104',
                'payment_terms': 'Net 45',
                'rating': 4
            },
            {
                'name': 'Office Solutions Pro',
                'contact_person': 'James Brown',
                'email': 'james@officesolutions.com',
                'phone': '+1-555-0105',
                'payment_terms': 'Net 30',
                'rating': 3
            }
        ]
        
        suppliers = {}
        for sup_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=sup_data['name'],
                defaults=sup_data
            )
            suppliers[sup_data['name']] = supplier
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')

        # Create inventory items
        items_data = [
            # Housekeeping Supplies
            {'name': 'Premium Bath Towels', 'category': 'Housekeeping Supplies', 'sku': 'HK001', 'unit': 'pcs', 'cost': 25.00, 'selling': 35.00, 'stock': 150, 'min': 50, 'max': 300, 'supplier': 'CleanPro Supplies Ltd'},
            {'name': 'Egyptian Cotton Bed Sheets', 'category': 'Housekeeping Supplies', 'sku': 'HK002', 'unit': 'set', 'cost': 45.00, 'selling': 65.00, 'stock': 80, 'min': 30, 'max': 150, 'supplier': 'CleanPro Supplies Ltd'},
            {'name': 'All-Purpose Cleaner', 'category': 'Housekeeping Supplies', 'sku': 'HK003', 'unit': 'bottle', 'cost': 8.50, 'selling': 12.00, 'stock': 200, 'min': 75, 'max': 400, 'supplier': 'CleanPro Supplies Ltd'},
            {'name': 'Vacuum Cleaner Bags', 'category': 'Housekeeping Supplies', 'sku': 'HK004', 'unit': 'pack', 'cost': 15.00, 'selling': 22.00, 'stock': 45, 'min': 20, 'max': 100, 'supplier': 'CleanPro Supplies Ltd'},
            {'name': 'Luxury Shampoo', 'category': 'Housekeeping Supplies', 'sku': 'HK005', 'unit': 'bottle', 'cost': 12.00, 'selling': 18.00, 'stock': 120, 'min': 50, 'max': 250, 'supplier': 'Luxury Amenities Inc'},
            
            # Food & Beverage
            {'name': 'Premium Coffee Beans', 'category': 'Food & Beverage', 'sku': 'FB001', 'unit': 'kg', 'cost': 35.00, 'selling': 50.00, 'stock': 25, 'min': 10, 'max': 60, 'supplier': 'Fresh Foods Distributors', 'perishable': True, 'shelf_life': 90},
            {'name': 'Fresh Orange Juice', 'category': 'Food & Beverage', 'sku': 'FB002', 'unit': 'ltr', 'cost': 8.00, 'selling': 15.00, 'stock': 40, 'min': 15, 'max': 80, 'supplier': 'Fresh Foods Distributors', 'perishable': True, 'shelf_life': 7},
            {'name': 'Artisan Bread', 'category': 'Food & Beverage', 'sku': 'FB003', 'unit': 'pcs', 'cost': 4.50, 'selling': 8.00, 'stock': 30, 'min': 20, 'max': 60, 'supplier': 'Fresh Foods Distributors', 'perishable': True, 'shelf_life': 3},
            {'name': 'Wine Selection', 'category': 'Food & Beverage', 'sku': 'FB004', 'unit': 'bottle', 'cost': 25.00, 'selling': 45.00, 'stock': 85, 'min': 30, 'max': 150, 'supplier': 'Fresh Foods Distributors'},
            {'name': 'Mineral Water', 'category': 'Food & Beverage', 'sku': 'FB005', 'unit': 'bottle', 'cost': 2.50, 'selling': 5.00, 'stock': 300, 'min': 100, 'max': 500, 'supplier': 'Fresh Foods Distributors'},
            
            # Maintenance Supplies
            {'name': 'HVAC Filters', 'category': 'Maintenance Supplies', 'sku': 'MT001', 'unit': 'pcs', 'cost': 35.00, 'selling': 50.00, 'stock': 24, 'min': 12, 'max': 48, 'supplier': 'Hotel Maintenance Co'},
            {'name': 'Plumbing Repair Kit', 'category': 'Maintenance Supplies', 'sku': 'MT002', 'unit': 'set', 'cost': 85.00, 'selling': 120.00, 'stock': 8, 'min': 5, 'max': 15, 'supplier': 'Hotel Maintenance Co'},
            {'name': 'LED Light Bulbs', 'category': 'Maintenance Supplies', 'sku': 'MT003', 'unit': 'pcs', 'cost': 12.00, 'selling': 18.00, 'stock': 150, 'min': 50, 'max': 300, 'supplier': 'Hotel Maintenance Co'},
            {'name': 'Paint (Interior)', 'category': 'Maintenance Supplies', 'sku': 'MT004', 'unit': 'ltr', 'cost': 28.00, 'selling': 40.00, 'stock': 20, 'min': 10, 'max': 40, 'supplier': 'Hotel Maintenance Co'},
            {'name': 'Power Tools Battery', 'category': 'Maintenance Supplies', 'sku': 'MT005', 'unit': 'pcs', 'cost': 45.00, 'selling': 65.00, 'stock': 12, 'min': 6, 'max': 24, 'supplier': 'Hotel Maintenance Co'},
            
            # Guest Amenities
            {'name': 'Welcome Gift Basket', 'category': 'Guest Amenities', 'sku': 'GA001', 'unit': 'pcs', 'cost': 35.00, 'selling': 55.00, 'stock': 25, 'min': 15, 'max': 50, 'supplier': 'Luxury Amenities Inc'},
            {'name': 'Spa Treatment Kit', 'category': 'Guest Amenities', 'sku': 'GA002', 'unit': 'set', 'cost': 65.00, 'selling': 95.00, 'stock': 18, 'min': 10, 'max': 35, 'supplier': 'Luxury Amenities Inc'},
            {'name': 'Premium Bathrobes', 'category': 'Guest Amenities', 'sku': 'GA003', 'unit': 'pcs', 'cost': 85.00, 'selling': 125.00, 'stock': 40, 'min': 20, 'max': 80, 'supplier': 'Luxury Amenities Inc'},
            {'name': 'Aromatherapy Candles', 'category': 'Guest Amenities', 'sku': 'GA004', 'unit': 'pcs', 'cost': 15.00, 'selling': 25.00, 'stock': 60, 'min': 30, 'max': 120, 'supplier': 'Luxury Amenities Inc'},
            
            # Office Supplies
            {'name': 'Printer Paper A4', 'category': 'Office Supplies', 'sku': 'OF001', 'unit': 'pack', 'cost': 8.00, 'selling': 12.00, 'stock': 50, 'min': 20, 'max': 100, 'supplier': 'Office Solutions Pro'},
            {'name': 'Ink Cartridges', 'category': 'Office Supplies', 'sku': 'OF002', 'unit': 'pcs', 'cost': 45.00, 'selling': 65.00, 'stock': 15, 'min': 8, 'max': 30, 'supplier': 'Office Solutions Pro'},
            {'name': 'Reception Folders', 'category': 'Office Supplies', 'sku': 'OF003', 'unit': 'pack', 'cost': 12.00, 'selling': 18.00, 'stock': 25, 'min': 15, 'max': 50, 'supplier': 'Office Solutions Pro'},
        ]
        
        items = {}
        for item_data in items_data:
            item, created = InventoryItem.objects.get_or_create(
                sku=item_data['sku'],
                defaults={
                    'name': item_data['name'],
                    'category': categories[item_data['category']],
                    'unit_of_measure': item_data['unit'],
                    'cost_price': Decimal(str(item_data['cost'])),
                    'selling_price': Decimal(str(item_data['selling'])),
                    'current_stock': Decimal(str(item_data['stock'])),
                    'minimum_stock': Decimal(str(item_data['min'])),
                    'maximum_stock': Decimal(str(item_data['max'])),
                    'reorder_point': Decimal(str(item_data['min'] + 5)),
                    'primary_supplier': suppliers[item_data['supplier']],
                    'is_perishable': item_data.get('perishable', False),
                    'shelf_life_days': item_data.get('shelf_life'),
                }
            )
            items[item_data['sku']] = item
            if created:
                self.stdout.write(f'Created item: {item.name}')

        # Create some stock movements
        movement_data = [
            {'item': 'HK001', 'type': 'in', 'qty': 50, 'cost': 25.00, 'reason': 'Initial stock purchase'},
            {'item': 'HK002', 'type': 'in', 'qty': 30, 'cost': 45.00, 'reason': 'Restocking bed sheets'},
            {'item': 'FB001', 'type': 'out', 'qty': -5, 'cost': 35.00, 'reason': 'Restaurant usage'},
            {'item': 'MT001', 'type': 'in', 'qty': 12, 'cost': 35.00, 'reason': 'Quarterly HVAC maintenance'},
            {'item': 'GA001', 'type': 'out', 'qty': -3, 'cost': 35.00, 'reason': 'VIP guest welcome gifts'},
            {'item': 'OF001', 'type': 'adjustment', 'qty': -2, 'cost': 8.00, 'reason': 'Stock count adjustment'},
        ]
        
        for mov_data in movement_data:
            StockMovement.objects.create(
                item=items[mov_data['item']],
                property=hotel,
                movement_type=mov_data['type'],
                quantity=Decimal(str(mov_data['qty'])),
                unit_cost=Decimal(str(mov_data['cost'])),
                reason=mov_data['reason'],
                created_by=admin_user
            )
        
        # Create a purchase order
        po, created = PurchaseOrder.objects.get_or_create(
            po_number='PO-2024-001',
            defaults={
                'supplier': suppliers['CleanPro Supplies Ltd'],
                'property': hotel,
                'order_date': date.today() - timedelta(days=5),
                'expected_delivery': date.today() + timedelta(days=3),
                'status': 'confirmed',
                'created_by': admin_user,
                'shipping_cost': Decimal('50.00'),
                'notes': 'Monthly housekeeping supplies order'
            }
        )
        
        # Add items to purchase order
        po_items = [
            {'item': 'HK001', 'qty': 100, 'price': 24.00},
            {'item': 'HK003', 'qty': 150, 'price': 8.00},
            {'item': 'HK005', 'qty': 80, 'price': 11.50},
        ]
        
        if created:  # Only add items if PO was just created
            for po_item_data in po_items:
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    item=items[po_item_data['item']],
                    quantity_ordered=Decimal(str(po_item_data['qty'])),
                    unit_price=Decimal(str(po_item_data['price']))
                )
            
            po.calculate_totals()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created inventory data:\n'
                f'- {len(categories)} categories\n'
                f'- {len(suppliers)} suppliers\n'
                f'- {len(items)} inventory items\n'
                f'- {len(movement_data)} stock movements\n'
                f'- 1 purchase order with {len(po_items)} items'
            )
        )