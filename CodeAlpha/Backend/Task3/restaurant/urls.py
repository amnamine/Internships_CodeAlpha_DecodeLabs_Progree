from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/menu/', views.get_menu, name='get_menu'),
    path('api/tables/', views.get_tables, name='get_tables'),
    path('api/orders/', views.get_orders, name='get_orders'),
    path('api/orders/create/', views.place_order, name='place_order'),
    path('api/orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('api/reservations/', views.get_reservations, name='get_reservations'),
    path('api/reservations/create/', views.make_reservation, name='make_reservation'),
    path('api/reservations/<int:reservation_id>/status/', views.update_reservation_status, name='update_reservation_status'),
    path('api/inventory/', views.get_inventory, name='get_inventory'),
    path('api/inventory/<int:item_id>/update-stock/', views.update_inventory_stock, name='update_inventory_stock'),
    path('api/tables/<int:table_id>/status/', views.update_table_status, name='update_table_status'),
    path('api/dashboard-stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
]
