from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('room/<str:room_code>/', views.room_view, name='room'),
    path('api/room/<str:room_code>/signal/send/', views.send_signal, name='send_signal'),
    path('api/room/<str:room_code>/signal/get/', views.get_signals, name='get_signals'),
    path('api/room/<str:room_code>/upload/', views.upload_file, name='upload_file'),
]
