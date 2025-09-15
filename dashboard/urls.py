from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Customer URLs
    path('klienti/', views.klienti, name='klienti'),
    path('klienti/nov/', views.customer_create, name='customer_create'),
    path('klienti/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('klienti/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('klienti/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Employee URLs
    path('slujiteli/', views.slujiteli, name='slujiteli'),
    path('slujiteli/nov/', views.employee_create, name='employee_create'),
    path('slujiteli/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('slujiteli/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('slujiteli/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # Days Off URLs
    path('slujiteli/otpusk/nov/', views.days_off_create, name='days_off_create'),
    path('slujiteli/otpusk/<int:pk>/edit/', views.days_off_edit, name='days_off_edit'),
    path('slujiteli/otpusk/<int:pk>/delete/', views.days_off_delete, name='days_off_delete'),
    
    # Other pages
    path('fakturi/', views.fakturi, name='fakturi'),
    path('poruchki/', views.poruchki, name='poruchki'),
    path('pregled-poruchki/', views.pregled_poruchki, name='pregled_poruchki'),
    path('slujiteli/', views.slujiteli, name='slujiteli'),
    path('sklad/', views.sklad, name='sklad'),
    path('sklad/nov/', views.sklad_create, name='sklad_create'),
    path('sklad/<int:pk>/', views.sklad_detail, name='sklad_detail'),
    path('sklad/<int:pk>/edit/', views.sklad_edit, name='sklad_edit'),
    path('sklad/<int:pk>/delete/', views.sklad_delete, name='sklad_delete'),
    path('sklad/autocomplete/', views.sklad_autocomplete, name='sklad_autocomplete'),
    path('sklad/import/', views.sklad_import, name='sklad_import'),
    path('sklad/import-stats/', views.sklad_import_stats, name='sklad_import_stats'),
    path('sklad/import-detail/<int:import_id>/', views.sklad_import_detail, name='sklad_import_detail'),
    path('sklad/import-delete/<int:import_id>/', views.sklad_import_delete, name='sklad_import_delete'),
    path('sklad/import-bulk-delete/', views.sklad_import_bulk_delete, name='sklad_import_bulk_delete'),
    path('get-weekly-planner/', views.get_weekly_planner, name='get_weekly_planner'),
    path('create-event/', views.create_event, name='create_event'),
    path('update-event/', views.update_event, name='update_event'),
    path('delete-event/', views.delete_event, name='delete_event'),
    path('cleanup-duplicate-events/', views.cleanup_duplicate_events, name='cleanup_duplicate_events'),
]
