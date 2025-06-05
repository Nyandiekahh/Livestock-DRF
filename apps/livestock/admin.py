# apps/livestock/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Cow, ChickenBatch, ChickenReduction

@admin.register(Cow)
class CowAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'tag_number', 'farm', 'breed', 'current_stage',
        'age_in_months', 'is_active', 'created_at'
    ]
    list_filter = [
        'farm', 'breed', 'current_stage', 'is_active', 
        'date_acquired', 'created_at'
    ]
    search_fields = ['name', 'tag_number', 'notes']
    ordering = ['farm', 'name']
    date_hierarchy = 'date_acquired'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farm', 'name', 'tag_number', 'breed', 'image')
        }),
        ('Dates and Acquisition', {
            'fields': ('date_of_birth', 'date_acquired', 'acquisition_cost')
        }),
        ('Current Status', {
            'fields': ('current_stage', 'weight', 'is_active')
        }),
        ('Lineage', {
            'fields': ('mother', 'father_info'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['age_in_months']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('farm', 'mother')
    
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Image'

@admin.register(ChickenBatch)
class ChickenBatchAdmin(admin.ModelAdmin):
    list_display = [
        'batch_name', 'farm', 'batch_type', 'current_count', 
        'initial_count', 'mortality_rate', 'date_acquired', 'is_active'
    ]
    list_filter = [
        'farm', 'batch_type', 'is_active', 'date_acquired'
    ]
    search_fields = ['batch_name', 'notes']
    ordering = ['farm', '-date_acquired']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farm', 'batch_name', 'batch_type')
        }),
        ('Count and Cost', {
            'fields': ('initial_count', 'current_count', 'acquisition_cost_per_bird')
        }),
        ('Dates', {
            'fields': ('date_acquired', 'expected_laying_start')
        }),
        ('Status and Notes', {
            'fields': ('is_active', 'notes')
        }),
    )
    
    readonly_fields = ['mortality_count', 'mortality_rate', 'total_cost']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('farm')

@admin.register(ChickenReduction)
class ChickenReductionAdmin(admin.ModelAdmin):
    list_display = ['batch', 'count', 'reason', 'date', 'created_at']
    list_filter = ['reason', 'date', 'batch__farm']
    search_fields = ['batch__batch_name', 'notes']
    ordering = ['-date']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('batch__farm')