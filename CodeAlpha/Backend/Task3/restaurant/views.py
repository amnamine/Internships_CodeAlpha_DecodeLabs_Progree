import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from .models import MenuItem, Table, Reservation, Order, OrderItem, InventoryItem, MenuItemIngredient

# Render landing page
def index(url_req):
    return render(url_req, 'restaurant/index.html')

# API Endpoints
def get_menu(request):
    menu_items = MenuItem.objects.all()
    data = []
    for item in menu_items:
        # Check if ingredients are sufficient
        has_ingredients = True
        for ingredient in item.ingredients.all():
            if ingredient.inventory_item.quantity < ingredient.quantity_needed:
                has_ingredients = False
                break
        
        # If not enough ingredients, mark unavailable
        if not has_ingredients and item.is_available:
            item.is_available = False
            item.save()
        elif has_ingredients and not item.is_available:
            item.is_available = True
            item.save()

        data.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': float(item.price),
            'category': item.category,
            'image_url': item.image_url or '',
            'is_available': item.is_available
        })
    return JsonResponse({'status': 'success', 'menu': data})


def get_tables(request):
    tables = Table.objects.all().order_by('table_number')
    data = [{
        'id': t.id,
        'table_number': t.table_number,
        'capacity': t.capacity,
        'status': t.status
    } for t in tables]
    return JsonResponse({'status': 'success', 'tables': data})


@csrf_exempt
def place_order(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        body = json.loads(request.body)
        table_id = body.get('table_id')
        items = body.get('items', [])  # list of {menu_item_id: X, quantity: Y}
        
        if not table_id or not items:
            return JsonResponse({'status': 'error', 'message': 'Missing table_id or items'}, status=400)
        
        table = get_object_or_404(Table, id=table_id)
        
        # Start transaction to ensure atomicity
        with transaction.atomic():
            # Calculate total & check stock
            total_amount = 0
            order_items_to_create = []
            inventory_updates = []  # List of tuples (InventoryItem, quantity_to_deduct)

            for order_item_req in items:
                menu_item_id = order_item_req.get('menu_item_id')
                qty = int(order_item_req.get('quantity', 1))
                if qty <= 0:
                    continue

                menu_item = get_object_or_404(MenuItem, id=menu_item_id)
                if not menu_item.is_available:
                    return JsonResponse({
                        'status': 'error', 
                        'message': f"{menu_item.name} is currently out of stock!"
                    }, status=400)

                # Check ingredients
                for ingredient in menu_item.ingredients.all():
                    qty_needed = ingredient.quantity_needed * qty
                    inv_item = ingredient.inventory_item
                    
                    if inv_item.quantity < qty_needed:
                        return JsonResponse({
                            'status': 'error',
                            'message': f"Insufficient stock for ingredient: {inv_item.name} (Requires {qty_needed} {inv_item.unit}, has {inv_item.quantity} {inv_item.unit})"
                        }, status=400)
                    
                    inventory_updates.append((inv_item, qty_needed))

                total_amount += menu_item.price * qty
                order_items_to_create.append((menu_item, qty, menu_item.price))

            # Deduct from inventory
            for inv_item, qty_deduct in inventory_updates:
                inv_item.quantity -= qty_deduct
                inv_item.save()

            # Create Order
            order = Order.objects.create(table=table, status='pending', total_amount=total_amount)
            
            # Create OrderItems
            for menu_item, qty, price in order_items_to_create:
                OrderItem.objects.create(order=order, menu_item=menu_item, quantity=qty, price=price)

            # Update Table Status
            table.status = 'occupied'
            table.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Order placed successfully!',
                'order_id': order.id
            })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def get_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    data = []
    for order in orders:
        items_data = [{
            'menu_item_name': item.menu_item.name,
            'quantity': item.quantity,
            'price': float(item.price)
        } for item in order.items.all()]

        data.append({
            'id': order.id,
            'table_number': order.table.table_number,
            'status': order.status,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'total_amount': float(order.total_amount),
            'items': items_data
        })
    return JsonResponse({'status': 'success', 'orders': data})


@csrf_exempt
def update_order_status(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        body = json.loads(request.body)
        new_status = body.get('status')
        if new_status not in ['pending', 'preparing', 'completed', 'cancelled']:
            return JsonResponse({'status': 'error', 'message': 'Invalid status value'}, status=400)

        order = get_object_or_404(Order, id=order_id)
        
        with transaction.atomic():
            old_status = order.status
            order.status = new_status
            order.save()

            # If completed or cancelled, free the table if no other active orders exist on that table
            if new_status in ['completed', 'cancelled']:
                active_orders = Order.objects.filter(table=order.table, status__in=['pending', 'preparing'])
                if not active_orders.exists():
                    order.table.status = 'available'
                    order.table.save()

            # If cancelled, optionally return items to inventory
            if new_status == 'cancelled' and old_status != 'cancelled':
                for item in order.items.all():
                    for ingredient in item.menu_item.ingredients.all():
                        qty_return = ingredient.quantity_needed * item.quantity
                        inv_item = ingredient.inventory_item
                        inv_item.quantity += qty_return
                        inv_item.save()

            return JsonResponse({'status': 'success', 'message': f'Order status updated to {new_status}'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def get_reservations(request):
    reservations = Reservation.objects.all().order_by('reservation_time')
    data = [{
        'id': r.id,
        'customer_name': r.customer_name,
        'customer_email': r.customer_email,
        'customer_phone': r.customer_phone,
        'table_number': r.table.table_number if r.table else 'Unassigned',
        'reservation_time': r.reservation_time.strftime('%Y-%m-%d %H:%M'),
        'number_of_guests': r.number_of_guests,
        'status': r.status
    } for r in reservations]
    return JsonResponse({'status': 'success', 'reservations': data})


@csrf_exempt
def make_reservation(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        body = json.loads(request.body)
        name = body.get('customer_name')
        email = body.get('customer_email')
        phone = body.get('customer_phone')
        guests = int(body.get('number_of_guests', 2))
        res_time_str = body.get('reservation_time')
        
        if not all([name, email, phone, res_time_str]):
            return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)
        
        reservation_time = timezone.datetime.fromisoformat(res_time_str)

        # Basic availability check: Find tables that match capacity and don't have overlapping reservations
        suitable_tables = Table.objects.filter(capacity__gte=guests).order_by('capacity')
        
        assigned_table = None
        for table in suitable_tables:
            # Check if this table has conflicting confirmed/pending reservations within 2 hours
            start_window = reservation_time - timezone.timedelta(hours=2)
            end_window = reservation_time + timezone.timedelta(hours=2)
            conflicts = Reservation.objects.filter(
                table=table,
                status__in=['pending', 'confirmed'],
                reservation_time__range=(start_window, end_window)
            )
            if not conflicts.exists():
                assigned_table = table
                break
        
        if not assigned_table:
            return JsonResponse({
                'status': 'error',
                'message': 'No tables available for the selected time and guest count.'
            }, status=400)

        with transaction.atomic():
            reservation = Reservation.objects.create(
                customer_name=name,
                customer_email=email,
                customer_phone=phone,
                table=assigned_table,
                reservation_time=reservation_time,
                number_of_guests=guests,
                status='pending'
            )
            # Reserve table
            assigned_table.status = 'reserved'
            assigned_table.save()

            return JsonResponse({
                'status': 'success',
                'message': f'Reservation requested successfully! Table {assigned_table.table_number} provisionally blocked.',
                'reservation_id': reservation.id
            })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def update_reservation_status(request, reservation_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        body = json.loads(request.body)
        new_status = body.get('status')
        if new_status not in ['pending', 'confirmed', 'cancelled']:
            return JsonResponse({'status': 'error', 'message': 'Invalid status value'}, status=400)

        reservation = get_object_or_404(Reservation, id=reservation_id)
        
        with transaction.atomic():
            reservation.status = new_status
            reservation.save()

            # Release table if reservation is cancelled
            if new_status == 'cancelled' and reservation.table:
                # check if table has other reservations/orders right now
                reservation.table.status = 'available'
                reservation.table.save()
            elif new_status == 'confirmed' and reservation.table:
                reservation.table.status = 'reserved'
                reservation.table.save()

            return JsonResponse({'status': 'success', 'message': f'Reservation status updated to {new_status}'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def get_inventory(request):
    inventory = InventoryItem.objects.all().order_by('name')
    data = [{
        'id': item.id,
        'name': item.name,
        'quantity': float(item.quantity),
        'unit': item.unit,
        'reorder_level': float(item.reorder_level),
        'needs_reorder': item.quantity <= item.reorder_level
    } for item in inventory]
    return JsonResponse({'status': 'success', 'inventory': data})


@csrf_exempt
def update_inventory_stock(request, item_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        body = json.loads(request.body)
        qty_add = float(body.get('quantity', 0))
        
        item = get_object_or_404(InventoryItem, id=item_id)
        item.quantity += qty_add
        if item.quantity < 0:
            item.quantity = 0
        item.save()

        return JsonResponse({
            'status': 'success', 
            'message': f'Updated {item.name} stock. New balance: {item.quantity} {item.unit}'
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def get_dashboard_stats(request):
    # Total Sales
    total_sales = Order.objects.filter(status='completed').aggregate(total=Sum('total_amount'))['total'] or 0.00
    
    # Active Orders Count
    active_orders = Order.objects.filter(status__in=['pending', 'preparing']).count()
    
    # Low stock items
    low_stock_count = 0
    inventory = InventoryItem.objects.all()
    for item in inventory:
        if item.quantity <= item.reorder_level:
            low_stock_count += 1
            
    # Table occupancy details
    tables = Table.objects.all()
    occupied = tables.filter(status='occupied').count()
    reserved = tables.filter(status='reserved').count()
    available = tables.filter(status='available').count()
    
    return JsonResponse({
        'status': 'success',
        'stats': {
            'total_sales': float(total_sales),
            'active_orders': active_orders,
            'low_stock_count': low_stock_count,
            'tables': {
                'occupied': occupied,
                'reserved': reserved,
                'available': available,
                'total': tables.count()
            }
        }
    })


@csrf_exempt
def update_table_status(request, table_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        body = json.loads(request.body)
        new_status = body.get('status')
        if new_status not in ['available', 'reserved', 'occupied']:
            return JsonResponse({'status': 'error', 'message': 'Invalid status value'}, status=400)

        table = get_object_or_404(Table, id=table_id)
        table.status = new_status
        table.save()

        return JsonResponse({
            'status': 'success',
            'message': f'Table {table.table_number} status updated to {new_status}'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

