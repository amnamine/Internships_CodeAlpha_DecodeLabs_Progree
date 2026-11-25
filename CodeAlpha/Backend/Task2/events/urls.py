from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('event/<slug:slug>/register/', views.register_event, name='register_event'),
    path('event/<slug:slug>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('event/create/new/', views.create_event, name='create_event'),
    path('event/<slug:slug>/edit/', views.edit_event, name='edit_event'),
    path('event/<slug:slug>/delete/', views.delete_event, name='delete_event'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
