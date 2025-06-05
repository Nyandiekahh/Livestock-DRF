# apps/financial/serializers.py
from rest_framework import serializers
from .models import Transaction, MonthlyFinancialSummary

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'farm', 'transaction_type', 'category', 'date', 'amount',
            'description', 'payment_method', 'reference_number',
            'milk_sale', 'feed_purchase', 'health_record', 'breeding_record',
            'recorded_by', 'notes', 'created_at', 'updated_at'
        ]

class MonthlyFinancialSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyFinancialSummary
        fields = [
            'id', 'farm', 'year', 'month', 'total_income', 'milk_sales_income',
            'livestock_sales_income', 'egg_sales_income', 'other_income',
            'total_expenses', 'feed_expenses', 'veterinary_expenses',
            'breeding_expenses', 'labor_expenses', 'other_expenses',
            'net_profit', 'profit_margin', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_income', 'milk_sales_income', 'livestock_sales_income',
            'egg_sales_income', 'other_income', 'total_expenses', 'feed_expenses',
            'veterinary_expenses', 'breeding_expenses', 'labor_expenses',
            'other_expenses', 'net_profit', 'profit_margin'
        ]