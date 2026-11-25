from django.db import models
from django.utils import timezone

class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('appetizer', 'Appetizer'),
        ('main', 'Main Course'),
        ('dessert', 'Dessert'),
        ('beverage', 'Beverage'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='main')
    image_url = models.CharField(max_length=255, blank=True, null=True, help_text="Optional external image URL or local static path")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Table(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
    ]
    table_number = models.IntegerField(unique=True)
    capacity = models.IntegerField(default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"Table {self.table_number} (Capacity: {self.capacity})"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    reservation_time = models.DateTimeField()
    number_of_guests = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - Table {self.table.table_number if self.table else 'Unassigned'} ({self.reservation_time})"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order #{self.id} - Table {self.table.table_number} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} for Order #{self.order.id}"


class InventoryItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    unit = models.CharField(max_length=20, default='units')  # e.g., kg, liters, units, pcs
    reorder_level = models.DecimalField(max_digits=8, decimal_places=2, default=5.00)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"


class MenuItemIngredient(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ingredients')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity_needed = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)

    class Meta:
        unique_together = ('menu_item', 'inventory_item')

    def __str__(self):
        return f"{self.quantity_needed} {self.inventory_item.unit} of {self.inventory_item.name} for {self.menu_item.name}"
