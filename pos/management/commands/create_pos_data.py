from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta, datetime
import random

from pos.models import (
    POSCategory, POSItem, POSOrder, POSOrderItem, POSPayment
)
from hotels.models import Hotel

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample POS data for Oceanview Resort & Spa'

    def handle(self, *args, **options):
        self.stdout.write('Creating POS sample data...')
        
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
            {'name': 'Beverages', 'description': 'Hot and cold drinks, cocktails, wines'},
            {'name': 'Appetizers', 'description': 'Starters and small plates'},
            {'name': 'Main Courses', 'description': 'Full meals and entrees'},
            {'name': 'Desserts', 'description': 'Sweet treats and desserts'},
            {'name': 'Room Service', 'description': 'In-room dining options'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = POSCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create menu items
        items_data = [
            # Beverages
            {'name': 'Espresso', 'category': 'Beverages', 'price': 4.50, 'cost': 1.20},
            {'name': 'Cappuccino', 'category': 'Beverages', 'price': 5.50, 'cost': 1.50},
            {'name': 'Fresh Orange Juice', 'category': 'Beverages', 'price': 6.00, 'cost': 2.00},
            {'name': 'House Wine (Glass)', 'category': 'Beverages', 'price': 12.00, 'cost': 4.00},
            {'name': 'Craft Beer', 'category': 'Beverages', 'price': 8.00, 'cost': 3.00},
            
            # Appetizers
            {'name': 'Caesar Salad', 'category': 'Appetizers', 'price': 14.00, 'cost': 5.00},
            {'name': 'Shrimp Cocktail', 'category': 'Appetizers', 'price': 18.00, 'cost': 8.00},
            {'name': 'Bruschetta', 'category': 'Appetizers', 'price': 12.00, 'cost': 4.00},
            
            # Main Courses
            {'name': 'Grilled Salmon', 'category': 'Main Courses', 'price': 28.00, 'cost': 12.00},
            {'name': 'Ribeye Steak', 'category': 'Main Courses', 'price': 35.00, 'cost': 18.00},
            {'name': 'Chicken Parmesan', 'category': 'Main Courses', 'price': 24.00, 'cost': 10.00},
            {'name': 'Vegetarian Pasta', 'category': 'Main Courses', 'price': 22.00, 'cost': 8.00},
            
            # Desserts
            {'name': 'Chocolate Cake', 'category': 'Desserts', 'price': 9.00, 'cost': 3.00},
            {'name': 'Tiramisu', 'category': 'Desserts', 'price': 10.00, 'cost': 3.50},
            {'name': 'Ice Cream', 'category': 'Desserts', 'price': 7.00, 'cost': 2.00},
            
            # Room Service
            {'name': 'Continental Breakfast', 'category': 'Room Service', 'price': 25.00, 'cost': 10.00},
            {'name': 'Club Sandwich', 'category': 'Room Service', 'price': 16.00, 'cost': 6.00},
            {'name': 'Fruit Platter', 'category': 'Room Service', 'price': 18.00, 'cost': 7.00},
        ]
        
        items = {}
        for item_data in items_data:
            item, created = POSItem.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    'category': categories[item_data['category']],
                    'price': Decimal(str(item_data['price'])),
                    'cost': Decimal(str(item_data['cost'])),
                    'is_available': True,
                    'is_active': True,
                }
            )
            items[item_data['name']] = item
            if created:
                self.stdout.write(f'Created item: {item.name}')

        # Create sample orders for the last 30 days
        orders_created = 0
        for days_ago in range(30):
            order_date = date.today() - timedelta(days=days_ago)
            
            # Create 3-8 orders per day
            daily_orders = random.randint(3, 8)
            
            for _ in range(daily_orders):
                # Generate order number
                order_number = f"POS{order_date.strftime('%Y%m%d')}{random.randint(1000, 9999)}"
                
                # Create order
                order = POSOrder.objects.create(
                    order_number=order_number,
                    order_type=random.choice(['dine_in', 'room_service', 'takeaway']),
                    customer_name=random.choice(['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'Room 205', 'Room 312']),
                    room_number=random.choice(['', '205', '312', '108', '401']) if random.random() > 0.5 else '',
                    table_number=random.choice(['', 'T1', 'T5', 'T12']) if random.random() > 0.3 else '',
                    status=random.choice(['served', 'served', 'served', 'cancelled']),  # Most orders are served
                    payment_status='paid',
                    created_by=admin_user,
                    order_time=datetime.combine(order_date, datetime.min.time().replace(
                        hour=random.randint(7, 22),
                        minute=random.randint(0, 59)
                    ))
                )
                
                # Add 1-4 items to each order
                order_items_count = random.randint(1, 4)
                selected_items = random.sample(list(items.values()), min(order_items_count, len(items)))
                
                for item in selected_items:
                    quantity = random.randint(1, 3)
                    POSOrderItem.objects.create(
                        order=order,
                        item=item,
                        quantity=quantity,
                        unit_price=item.price,
                        total_price=item.price * quantity
                    )
                
                # Calculate order totals
                order.calculate_totals()
                
                # Create payment
                payment_method = random.choice(['cash', 'card', 'room_charge', 'digital_wallet'])
                POSPayment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    processed_by=admin_user
                )
                
                orders_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created POS data:\n'
                f'- {len(categories)} categories\n'
                f'- {len(items)} menu items\n'
                f'- {orders_created} orders with payments\n'
                f'- Data spans last 30 days'
            )
        )