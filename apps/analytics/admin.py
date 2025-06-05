# apps/analytics/admin.py
from django.contrib import admin
from .models import ProductionReport

@admin.register(ProductionReport)
class ProductionReportAdmin(admin.ModelAdmin):
    list_display = [
        'farm', 'report_type', 'start_date', 'end_date',
        'generated_by', 'created_at'
    ]
    list_filter = ['farm', 'report_type', 'start_date', 'created_at']
    search_fields = ['farm__name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    readonly_fields = ['report_data', 'file_path']