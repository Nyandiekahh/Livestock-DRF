# apps/breeding/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import BreedingRecord, HeatDetection

@admin.register(BreedingRecord)
class BreedingRecordAdmin(admin.ModelAdmin):
    list_display = [
        'cow', 'breeding_date', 'breeding_method', 'pregnancy_confirmed',
        'expected_calving_date', 'actual_calving_date', 'days_to_calving',
        'is_overdue'
    ]
    list_filter = [
        'breeding_method', 'pregnancy_confirmed', 'breeding_date',
        'cow__farm'
    ]
    search_fields = ['cow__name', 'cow__tag_number', 'bull_info', 'ai_technician']
    ordering = ['-breeding_date']
    date_hierarchy = 'breeding_date'
    
    fieldsets = (
        ('Cow Information', {
            'fields': ('cow',)
        }),
        ('Breeding Details', {
            'fields': (
                'heat_detected_date', 'breeding_date', 'breeding_method',
                'bull_info', 'ai_technician', 'breeding_cost'
            )
        }),
        ('Pregnancy', {
            'fields': (
                'pregnancy_confirmed', 'pregnancy_test_date',
                'expected_calving_date'
            )
        }),
        ('Calving', {
            'fields': (
                'actual_calving_date', 'calving_complications', 'calf_born'
            )
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
    )
    
    def days_to_calving(self, obj):
        days = obj.days_to_calving
        if days is None:
            return "-"
        if days < 0:
            return format_html('<span style="color: red;">Overdue by {} days</span>', abs(days))
        elif days <= 7:
            return format_html('<span style="color: orange;">{} days</span>', days)
        else:
            return f"{days} days"
    days_to_calving.short_description = 'Days to Calving'
    
    def is_overdue(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">Yes</span>')
        return "No"
    is_overdue.short_description = 'Overdue'
    is_overdue.boolean = True

@admin.register(HeatDetection)
class HeatDetectionAdmin(admin.ModelAdmin):
    list_display = [
        'cow', 'heat_date', 'heat_intensity', 'bred_this_cycle',
        'breeding_record', 'detected_by'
    ]
    list_filter = [
        'heat_intensity', 'bred_this_cycle', 'heat_date', 'cow__farm'
    ]
    search_fields = ['cow__name', 'cow__tag_number', 'notes']
    ordering = ['-heat_date']
    date_hierarchy = 'heat_date'