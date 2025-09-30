"""
Django Admin configuration for Car Service Management System
"""
from django.contrib import admin
from .models import Sklad, Customer, Car, Order, OrderItem, Event


@admin.register(Sklad)
class SkladAdmin(admin.ModelAdmin):
    """Admin interface for Sklad (Warehouse/Inventory)"""
    list_display = ('article_number', 'name', 'unit', 'quantity', 'purchase_price', 'total_value', 'is_active')
    list_filter = ('is_active', 'unit', 'created_at')
    search_fields = ('article_number', 'name')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('article_number',)
    
    fieldsets = (
        ('Основна информация', {
            'fields': ('article_number', 'name', 'unit')
        }),
        ('Количество и цени', {
            'fields': ('quantity', 'purchase_price')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Системна информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_value(self, obj):
        """Display calculated total value"""
        return f"{obj.total_value:.2f} лв."
    total_value.short_description = 'Стойност'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin interface for Customers"""
    list_display = ('number', 'customer_name', 'customer_mol', 'customer_taxno')
    list_filter = ('customer_doctype', 'created_at')
    search_fields = ('number', 'customer_name', 'customer_mol', 'customer_taxno', 'customer_address_1')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('number',)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    """Admin interface for Cars"""
    list_display = ('plate_number', 'brand_model', 'customer', 'vin')
    list_filter = ('created_at',)
    search_fields = ('plate_number', 'vin', 'brand_model', 'customer__customer_name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('customer',)
    ordering = ('plate_number',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Orders"""
    list_display = ('order_number', 'order_date', 'client_name', 'car_plate_number', 'status', 'total_with_vat')
    list_filter = ('status', 'order_date', 'created_at')
    search_fields = ('order_number', 'client_name', 'car_plate_number', 'car_vin')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'order_date'
    ordering = ('-order_date',)
    
    def total_with_vat(self, obj):
        """Display total price with VAT"""
        return f"{obj.price_with_vat:.2f} лв." if obj.price_with_vat else "0.00 лв."
    total_with_vat.short_description = 'Обща стойност'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for Order Items"""
    list_display = ('order', 'name', 'unit', 'quantity', 'purchase_price', 'total_price', 'is_labor')
    list_filter = ('is_labor', 'unit')
    search_fields = ('name', 'article_number', 'order__order_number')
    # Don't use autocomplete for order/sklad_item to avoid circular dependencies
    # autocomplete_fields = ('order', 'sklad_item')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for Events/Calendar"""
    list_display = ('title', 'start_datetime', 'end_datetime', 'is_all_day', 'event_type')
    list_filter = ('is_all_day', 'event_type', 'start_datetime')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_datetime'
    ordering = ('-start_datetime',)
