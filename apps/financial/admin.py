# apps/financial/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Transaction, MonthlyFinancialSummary

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'farm', 'transaction_type', 'category', 'date',
        'amount', 'payment_method', 'recorded_by'
    ]
    list_filter = [
        'farm', 'transaction_type', 'category', 'payment_method', 'date'
    ]
    search_fields = ['description', 'reference_number', 'notes']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('farm', 'transaction_type', 'category', 'date', 'amount')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'reference_number')
        }),
        ('Description', {
            'fields': ('description', 'notes')
        }),
        ('Related Records', {
            'fields': (
                'milk_sale', 'feed_purchase', 'health_record', 'breeding_record'
            ),
            'classes': ('collapse',)
        }),
        ('Recording Information', {
            'fields': ('recorded_by',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'farm', 'recorded_by'
        )

@admin.register(MonthlyFinancialSummary)
class MonthlyFinancialSummaryAdmin(admin.ModelAdmin):
    list_display = [
        'farm', 'year', 'month', 'total_income', 'total_expenses',
        'net_profit', 'profit_margin_display'
    ]
    list_filter = ['farm', 'year', 'month']
    ordering = ['-year', '-month', 'farm']
    
    fieldsets = (
        ('Period', {
            'fields': ('farm', 'year', 'month')
        }),
        ('Income Breakdown', {
            'fields': (
                'total_income', 'milk_sales_income', 'livestock_sales_income',
                'egg_sales_income', 'other_income'
            )
        }),
        ('Expense Breakdown', {
            'fields': (
                'total_expenses', 'feed_expenses', 'veterinary_expenses',
                'breeding_expenses', 'labor_expenses', 'other_expenses'
            )
        }),
        ('Summary', {
            'fields': ('net_profit', 'profit_margin')
        }),
    )
    
    readonly_fields = [
        'total_income', 'milk_sales_income', 'livestock_sales_income',
        'egg_sales_income', 'other_income', 'total_expenses', 'feed_expenses',
        'veterinary_expenses', 'breeding_expenses', 'labor_expenses',
        'other_expenses', 'net_profit', 'profit_margin'
    ]
    
    actions = ['recalculate_summaries']
    
    def profit_margin_display(self, obj):
        if obj.profit_margin >= 0:
            color = 'green'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.2f}%</span>',
            color,
            obj.profit_margin
        )
    profit_margin_display.short_description = 'Profit Margin'
    
    def recalculate_summaries(self, request, queryset):
        for summary in queryset:
            summary.calculate_summary()
        self.message_user(
            request,
            f"Successfully recalculated {queryset.count()} summaries."
        )
    recalculate_summaries.short_description = "Recalculate selected summaries"
