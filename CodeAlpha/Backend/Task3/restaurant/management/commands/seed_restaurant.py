import os
from django.core.management.base import BaseCommand
from restaurant.models import MenuItem, Table, InventoryItem, MenuItemIngredient

class Command(BaseCommand):
    help = "Seed the restaurant database with mock menu items, tables, inventory, and ingredients."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Clear existing data
        MenuItemIngredient.objects.all().delete()
        MenuItem.objects.all().delete()
        Table.objects.all().delete()
        InventoryItem.objects.all().delete()

        # 2. Seed Tables
        tables_data = [
            {'table_number': 1, 'capacity': 2, 'status': 'available'},
            {'table_number': 2, 'capacity': 2, 'status': 'available'},
            {'table_number': 3, 'capacity': 4, 'status': 'available'},
            {'table_number': 4, 'capacity': 4, 'status': 'available'},
            {'table_number': 5, 'capacity': 6, 'status': 'available'},
            {'table_number': 6, 'capacity': 8, 'status': 'available'},
        ]
        for t in tables_data:
            Table.objects.create(**t)
        self.stdout.write(f"Created {len(tables_data)} tables.")

        # 3. Seed Inventory Items
        inventory_data = [
            {'name': 'Beef Patty', 'quantity': 50, 'unit': 'pcs', 'reorder_level': 10},
            {'name': 'Burger Bun', 'quantity': 60, 'unit': 'pcs', 'reorder_level': 10},
            {'name': 'Cheese Slice', 'quantity': 100, 'unit': 'pcs', 'reorder_level': 20},
            {'name': 'Tomato', 'quantity': 15.0, 'unit': 'kg', 'reorder_level': 3.0},
            {'name': 'Lettuce', 'quantity': 10.0, 'unit': 'kg', 'reorder_level': 2.0},
            {'name': 'Chicken Breast', 'quantity': 30, 'unit': 'pcs', 'reorder_level': 8},
            {'name': 'Pasta', 'quantity': 25.0, 'unit': 'kg', 'reorder_level': 5.0},
            {'name': 'Truffle Oil', 'quantity': 2.0, 'unit': 'liters', 'reorder_level': 0.5},
            {'name': 'Salmon Fillet', 'quantity': 20, 'unit': 'pcs', 'reorder_level': 5},
            {'name': 'Potato', 'quantity': 40.0, 'unit': 'kg', 'reorder_level': 10.0},
            {'name': 'Espresso Beans', 'quantity': 5.0, 'unit': 'kg', 'reorder_level': 1.0},
            {'name': 'Milk', 'quantity': 20.0, 'unit': 'liters', 'reorder_level': 5.0},
            {'name': 'Chocolate', 'quantity': 10.0, 'unit': 'kg', 'reorder_level': 2.0},
        ]
        inventory_items = {}
        for inv in inventory_data:
            item = InventoryItem.objects.create(**inv)
            inventory_items[inv['name']] = item
        self.stdout.write(f"Created {len(inventory_data)} inventory items.")

        # 4. Seed Menu Items
        menu_items_data = [
            # Appetizers
            {
                'name': 'Truffle Fries',
                'description': 'Crispy golden fries tossed in aromatic truffle oil, parmesan, and fresh parsley.',
                'price': 8.50,
                'category': 'appetizer',
                'is_available': True,
                'ingredients': [
                    ('Potato', 0.3),  # 0.3 kg
                    ('Truffle Oil', 0.02),  # 0.02 L
                ]
            },
            {
                'name': 'Bruschetta Classica',
                'description': 'Toasted sourdough topped with vine-ripened tomatoes, garlic, basil, and balsamic glaze.',
                'price': 7.00,
                'category': 'appetizer',
                'is_available': True,
                'ingredients': [
                    ('Tomato', 0.15),
                ]
            },
            # Mains
            {
                'name': 'The Royale Burger',
                'description': 'Premium beef patty, cheddar, heirloom tomato, crisp lettuce, and signature sauce on a brioche bun.',
                'price': 15.50,
                'category': 'main',
                'is_available': True,
                'ingredients': [
                    ('Beef Patty', 1),
                    ('Burger Bun', 1),
                    ('Cheese Slice', 1),
                    ('Tomato', 0.05),
                    ('Lettuce', 0.02),
                ]
            },
            {
                'name': 'Pan-Seared Salmon',
                'description': 'Fresh Atlantic salmon served over a bed of baby potatoes and seasonal greens.',
                'price': 22.00,
                'category': 'main',
                'is_available': True,
                'ingredients': [
                    ('Salmon Fillet', 1),
                    ('Potato', 0.2),
                    ('Lettuce', 0.05),
                ]
            },
            {
                'name': 'Truffle Mushroom Pasta',
                'description': 'Fettuccine in a rich creamy mushroom sauce infused with white truffle oil.',
                'price': 18.00,
                'category': 'main',
                'is_available': True,
                'ingredients': [
                    ('Pasta', 0.15),
                    ('Truffle Oil', 0.01),
                ]
            },
            # Desserts
            {
                'name': 'Molten Lava Cake',
                'description': 'Warm dark chocolate cake with a gooey liquid chocolate center, served with vanilla ice cream.',
                'price': 9.00,
                'category': 'dessert',
                'is_available': True,
                'ingredients': [
                    ('Chocolate', 0.1),
                    ('Milk', 0.05),
                ]
            },
            # Beverages
            {
                'name': 'Artisanal Latte',
                'description': 'Freshly brewed espresso with steamed velvety milk and micro-foam art.',
                'price': 4.50,
                'category': 'beverage',
                'is_available': True,
                'ingredients': [
                    ('Espresso Beans', 0.02),
                    ('Milk', 0.25),
                ]
            },
        ]

        for item_data in menu_items_data:
            ingredients = item_data.pop('ingredients')
            menu_item = MenuItem.objects.create(**item_data)
            for ing_name, qty in ingredients:
                MenuItemIngredient.objects.create(
                    menu_item=menu_item,
                    inventory_item=inventory_items[ing_name],
                    quantity_needed=qty
                )
        self.stdout.write(f"Created {len(menu_items_data)} menu items with ingredients linked.")
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
