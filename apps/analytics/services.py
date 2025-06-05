# apps/analytics/services.py
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from apps.production.models import MilkProduction, EggProduction
from apps.livestock.models import Cow, ChickenBatch
from apps.feeds.models import DailyFeedConsumption, ChickenFeedConsumption
from apps.financial.models import Transaction

class AnalyticsService:
    """Service class for generating analytics and reports"""
    
    @staticmethod
    def get_milk_production_stats(farm, start_date, end_date):
        """Get milk production statistics for a farm and date range"""
        milk_records = MilkProduction.objects.filter(
            cow__farm=farm,
            date__range=[start_date, end_date],
            is_deleted=False
        )
        
        stats = milk_records.aggregate(
            total_production=Sum('quantity_liters'),
            average_per_cow=Avg('quantity_liters'),
            total_records=Count('id'),
            unique_cows=Count('cow', distinct=True)
        )
        
        # Daily breakdown
        daily_stats = {}
        for record in milk_records:
            date_str = record.date.strftime('%Y-%m-%d')
            if date_str not in daily_stats:
                daily_stats[date_str] = {
                    'morning': 0, 'afternoon': 0, 'evening': 0, 'total': 0
                }
            daily_stats[date_str][record.session] += float(record.quantity_liters)
            daily_stats[date_str]['total'] += float(record.quantity_liters)
        
        return {
            'summary': stats,
            'daily_breakdown': daily_stats,
            'period': f"{start_date} to {end_date}"
        }
    
    @staticmethod
    def get_egg_production_stats(farm, start_date, end_date):
        """Get egg production statistics for a farm and date range"""
        egg_records = EggProduction.objects.filter(
            batch__farm=farm,
            date__range=[start_date, end_date],
            is_deleted=False
        )
        
        stats = egg_records.aggregate(
            total_eggs_collected=Sum('eggs_collected'),
            total_broken_eggs=Sum('broken_eggs'),
            total_eggs_sold=Sum('eggs_sold'),
            total_eggs_consumed=Sum('eggs_consumed'),
            average_daily_collection=Avg('eggs_collected')
        )
        
        # Calculate usable eggs
        stats['total_usable_eggs'] = (
            (stats['total_eggs_collected'] or 0) - 
            (stats['total_broken_eggs'] or 0)
        )
        
        return {
            'summary': stats,
            'period': f"{start_date} to {end_date}"
        }
    
    @staticmethod
    def get_feed_consumption_stats(farm, start_date, end_date):
        """Get feed consumption statistics"""
        cow_feeds = DailyFeedConsumption.objects.filter(
            cow__farm=farm,
            date__range=[start_date, end_date],
            is_deleted=False
        )
        
        chicken_feeds = ChickenFeedConsumption.objects.filter(
            batch__farm=farm,
            date__range=[start_date, end_date],
            is_deleted=False
        )
        
        cow_stats = cow_feeds.aggregate(
            total_dairy_meal=Sum('dairy_meal_kg'),
            total_maize_germ=Sum('maize_germ_kg'),
            total_maclic_supa=Sum('maclic_supa_kg'),
            total_maclic_plus=Sum('maclic_plus_kg'),
            total_roughage=Sum('napier_hay_silage_kg')
        )
        
        chicken_stats = chicken_feeds.aggregate(
            total_chicken_feed=Sum('feed_quantity_kg'),
            total_feed_cost=Sum('feed_cost')
        )
        
        return {
            'cow_consumption': cow_stats,
            'chicken_consumption': chicken_stats,
            'period': f"{start_date} to {end_date}"
        }
    
    @staticmethod
    def get_financial_summary(farm, start_date, end_date):
        """Get financial summary for a farm and date range"""
        transactions = Transaction.objects.filter(
            farm=farm,
            date__range=[start_date, end_date],
            is_deleted=False
        )
        
        income = transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        expenses = transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        net_profit = income - expenses
        profit_margin = (net_profit / income * 100) if income > 0 else 0
        
        return {
            'total_income': income,
            'total_expenses': expenses,
            'net_profit': net_profit,
            'profit_margin': profit_margin,
            'period': f"{start_date} to {end_date}"
        }
