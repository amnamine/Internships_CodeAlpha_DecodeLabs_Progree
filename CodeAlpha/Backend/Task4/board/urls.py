from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('job/<int:pk>/', views.job_detail_view, name='job_detail'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('post-job/', views.post_job_view, name='post_job'),
    path('apply/<int:job_id>/', views.apply_job_view, name='apply_job'),
    path('application/status/<int:app_id>/', views.update_application_status, name='update_application_status'),
]
