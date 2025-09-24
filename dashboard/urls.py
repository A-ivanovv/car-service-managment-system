from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Customer URLs
    path('klienti/', views.klienti, name='klienti'),
    path('klienti/nov/', views.customer_create, name='customer_create'),
    path('klienti/get-next-number/', views.get_next_customer_number, name='get_next_customer_number'),
    path('klienti/search-ajax/', views.customer_search_ajax, name='customer_search_ajax'),
    path('pregled-poruchki/search-ajax/', views.order_search_ajax, name='order_search_ajax'),
    path('fakturi/search-ajax/', views.invoice_search_ajax, name='invoice_search_ajax'),
    path('fakturi/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('klienti/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('klienti/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('klienti/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('koli/<int:car_id>/poruchki/', views.car_orders, name='car_orders'),
    
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
    
    # Order URLs
    path('poruchki/', views.poruchki, name='poruchki'),
    path('poruchki/nov/', views.order_create, name='order_create'),
    path('poruchki/<int:pk>/', views.order_detail, name='order_detail'),
    path('poruchki/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('poruchki/<int:pk>/delete/', views.order_delete, name='order_delete'),
    
    # Order autocomplete URLs
    path('poruchki/autocomplete/car-vin/', views.order_autocomplete_car_vin, name='order_autocomplete_car_vin'),
    path('poruchki/autocomplete/car-plate/', views.order_autocomplete_car_plate, name='order_autocomplete_car_plate'),
    path('poruchki/autocomplete/client/', views.order_autocomplete_client, name='order_autocomplete_client'),
    path('poruchki/autocomplete/sklad/', views.order_autocomplete_sklad, name='order_autocomplete_sklad'),
    path('poruchki/get-car-info/', views.order_get_car_info, name='order_get_car_info'),
    path('poruchki/get-client-info/', views.order_get_client_info, name='order_get_client_info'),
    
    # Order sklad modal URLs
    path('poruchki/sklad-modal-data/', views.order_sklad_modal_data, name='order_sklad_modal_data'),
    path('poruchki/sklad-units/', views.order_sklad_units, name='order_sklad_units'),
    
    # Currency rate URL
    path('poruchki/currency-rate/', views.currency_rate, name='currency_rate'),
    
    # Order PDF generation URLs
    path('poruchki/<int:pk>/generate-offer/', views.order_generate_offer, name='order_generate_offer'),
    path('poruchki/<int:pk>/generate-invoice/', views.order_generate_invoice, name='order_generate_invoice'),
    
    # Order preview and conversion URLs
    path('poruchki/<int:pk>/preview-offer/', views.order_preview_offer, name='order_preview_offer'),
    path('poruchki/<int:pk>/preview-invoice/', views.order_preview_invoice, name='order_preview_invoice'),
    path('poruchki/<int:pk>/convert-to-invoice/', views.order_convert_to_invoice, name='order_convert_to_invoice'),
    
    # Other pages
    path('fakturi/', views.fakturi, name='fakturi'),
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
