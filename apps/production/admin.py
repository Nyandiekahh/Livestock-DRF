# apps/production/admin.py
from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from .models import (
    MilkProduction, DailyMilkSummary, MilkSale, 
    EggProduction, ChickHatching
)

@admin.register(MilkProduction)
class MilkProductionAdmin(admin.ModelAdmin):
    list_display = [
        'cow', 'date', 'session', 'quantity_liters', 
        'quality_grade', 'recorded_by', 'created_at'
    ]
    list_filter = [
        'date', 'session', 'quality_grade', 'cow__farm',
        'cow__current_stage', 'created_at'
    ]
    search_fields = ['cow__name', 'cow__tag_number', 'notes']
    ordering = ['-date', 'cow__name', 'session']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Production Details', {
            'fields': ('cow', 'date', 'session', 'quantity_liters', 'quality_grade')
        }),
        ('Recording Information', {
            'fields': ('recorded_by', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cow__farm', 'recorded_by'
        )

@admin.register(DailyMilkSummary)
class DailyMilkSummaryAdmin(admin.ModelAdmin):
    list_display = [
        'farm', 'date', 'total_daily', 'cows_milked', 
        'average_per_cow', 'created_at'
    ]
    list_filter = ['farm', 'date']
    ordering = ['-date', 'farm']
    date_hierarchy = 'date'
    readonly_fields = [
        'total_morning', 'total_afternoon', 'total_evening',
        'total_daily', 'cows_milked', 'average_per_cow'
    ]
    
    actions = ['recalculate_summaries']
    
    def recalculate_summaries(self, request, queryset):
        for summary in queryset:
            summary.calculate_summary()
        self.message_user(
            request, 
            f"Successfully recalculated {queryset.count()} summaries."
        )
    recalculate_summaries.short_description = "Recalculate selected summaries"

@admin.register(MilkSale)
class MilkSaleAdmin(admin.ModelAdmin):
    list_display = [
        'farm', 'date', 'quantity_liters', 'price_per_liter',
        'total_amount', 'buyer_name', 'payment_method', 'recorded_by'
    ]
    list_filter = ['farm', 'date', 'payment_method']
    search_fields = ['buyer_name', 'buyer_contact', 'notes']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Sale Details', {
            'fields': ('farm', 'date', 'quantity_liters', 'price_per_liter')
        }),
        ('Buyer Information', {
            'fields': ('buyer_name', 'buyer_contact', 'payment_method')
        }),
        ('Recording Information', {
            'fields': ('recorded_by', 'notes')
        }),
    )
    
    readonly_fields = ['total_amount']

@admin.register(EggProduction)
class EggProductionAdmin(admin.ModelAdmin):
    list_display = [
        'batch', 'date', 'eggs_collected', 'broken_eggs',
        'usable_eggs', 'eggs_sold', 'recorded_by'
    ]
    list_filter = ['date', 'batch__farm', 'batch__batch_type']
    search_fields = ['batch__batch_name', 'notes']
    ordering = ['-date', 'batch__batch_name']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'batch__farm', 'recorded_by'
        )

@admin.register(ChickHatching)
class ChickHatchingAdmin(admin.ModelAdmin):
    list_display = [
        'batch', 'date', 'eggs_set_for_hatching', 'chicks_hatched',
        'hatching_rate', 'recorded_by'
    ]
    list_filter = ['date', 'batch__farm']
    search_fields = ['batch__batch_name', 'notes']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    def hatching_rate(self, obj):
        return f"{obj.hatching_rate:.1f}%"
    hatching_rate.short_description = 'Hatching Rate'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'batch__farm', 'recorded_by'
        )
