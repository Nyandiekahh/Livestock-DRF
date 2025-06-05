# apps/feeds/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import (
    FeedType, FeedPurchase, DailyFeedConsumption,
    ChickenFeedConsumption, FeedInventory
)

@admin.register(FeedType)
class FeedTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit_of_measurement', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'unit_of_measurement']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']

@admin.register(FeedPurchase)
class FeedPurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'feed_type', 'farm', 'purchase_date', 'quantity',
        'unit_price', 'total_cost', 'remaining_quantity',
        'consumption_percentage', 'is_finished'
    ]
    list_filter = [
        'farm', 'feed_type__category', 'purchase_date',
        'is_finished', 'feed_type'
    ]
    search_fields = ['supplier_name', 'supplier_contact', 'notes']
    ordering = ['-purchase_date']
    date_hierarchy = 'purchase_date'
    
    fieldsets = (
        ('Purchase Details', {
            'fields': ('farm', 'feed_type', 'purchase_date', 'expiry_date')
        }),
        ('Quantity and Pricing', {
            'fields': ('quantity', 'unit_price', 'transport_cost')
        }),
        ('Supplier Information', {
            'fields': ('supplier_name', 'supplier_contact')
        }),
        ('Stock Management', {
            'fields': ('remaining_quantity', 'is_finished')
        }),
        ('Additional Information', {
            'fields': ('recorded_by', 'notes')
        }),
    )
    
    readonly_fields = ['total_cost', 'consumption_percentage']
    actions = ['mark_as_finished']
    
    def mark_as_finished(self, request, queryset):
        updated = queryset.update(is_finished=True, remaining_quantity=0)
        self.message_user(
            request,
            f"Successfully marked {updated} purchases as finished."
        )
    mark_as_finished.short_description = "Mark selected purchases as finished"
    
    def consumption_percentage(self, obj):
        percentage = obj.consumption_percentage
        color = 'green' if percentage < 50 else 'orange' if percentage < 80 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            percentage
        )
    consumption_percentage.short_description = 'Consumed %'

@admin.register(DailyFeedConsumption)
class DailyFeedConsumptionAdmin(admin.ModelAdmin):
    list_display = [
        'cow', 'date', 'total_concentrate_kg', 'total_mineral_kg',
        'napier_hay_silage_kg', 'total_feed_kg', 'recorded_by'
    ]
    list_filter = ['date', 'cow__farm', 'cow__current_stage']
    search_fields = ['cow__name', 'cow__tag_number', 'notes']
    ordering = ['-date', 'cow__name']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('cow', 'date')
        }),
        ('Concentrates (kg)', {
            'fields': ('dairy_meal_kg', 'maize_germ_kg')
        }),
        ('Minerals (kg)', {
            'fields': ('maclic_supa_kg', 'maclic_plus_kg')
        }),
        ('Roughage (kg)', {
            'fields': ('napier_hay_silage_kg',)
        }),
        ('Recording Information', {
            'fields': ('recorded_by', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cow__farm', 'recorded_by'
        )

@admin.register(ChickenFeedConsumption)
class ChickenFeedConsumptionAdmin(admin.ModelAdmin):
    list_display = [
        'batch', 'date', 'feed_quantity_kg', 'feed_cost',
        'cost_per_bird', 'recorded_by'
    ]
    list_filter = ['date', 'batch__farm', 'batch__batch_type']
    search_fields = ['batch__batch_name', 'notes']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'batch__farm', 'recorded_by'
        )

@admin.register(FeedInventory)
class FeedInventoryAdmin(admin.ModelAdmin):
    list_display = [
        'farm', 'feed_type', 'current_stock', 'minimum_stock_level',
        'stock_status', 'last_updated'
    ]
    list_filter = ['farm', 'feed_type__category', 'feed_type']
    search_fields = ['feed_type__name']
    ordering = ['farm', 'feed_type__category', 'feed_type__name']
    
    def stock_status(self, obj):
        status = obj.stock_status
        colors = {
            'Low Stock': 'red',
            'Running Low': 'orange',
            'Good Stock': 'green'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, 'black'),
            status
        )
    stock_status.short_description = 'Stock Status'
    
    actions = ['check_low_stock']
    
    def check_low_stock(self, request, queryset):
        low_stock_items = queryset.filter(
            current_stock__lte=models.F('minimum_stock_level')
        )
        count = low_stock_items.count()
        if count > 0:
            self.message_user(
                request,
                f"Found {count} items with low stock levels.",
                level='warning'
            )
        else:
            self.message_user(request, "No items with low stock found.")
    check_low_stock.short_description = "Check for low stock items"
