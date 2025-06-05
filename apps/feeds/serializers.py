# apps/feeds/serializers.py
from rest_framework import serializers
from .models import (
    FeedType, FeedPurchase, DailyFeedConsumption,
    ChickenFeedConsumption, FeedInventory
)

class FeedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedType
        fields = '__all__'

class FeedPurchaseSerializer(serializers.ModelSerializer):
    consumption_percentage = serializers.ReadOnlyField()
    feed_type_name = serializers.CharField(source='feed_type.name', read_only=True)
    
    class Meta:
        model = FeedPurchase
        fields = [
            'id', 'farm', 'feed_type', 'feed_type_name', 'purchase_date',
            'quantity', 'unit_price', 'total_cost', 'transport_cost',
            'supplier_name', 'supplier_contact', 'remaining_quantity',
            'is_finished', 'expiry_date', 'consumption_percentage',
            'recorded_by', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_cost']

class DailyFeedConsumptionSerializer(serializers.ModelSerializer):
    cow_name = serializers.CharField(source='cow.name', read_only=True)
    total_concentrate_kg = serializers.ReadOnlyField()
    total_mineral_kg = serializers.ReadOnlyField()
    total_feed_kg = serializers.ReadOnlyField()
    
    class Meta:
        model = DailyFeedConsumption
        fields = [
            'id', 'cow', 'cow_name', 'date', 'dairy_meal_kg', 'maize_germ_kg',
            'maclic_supa_kg', 'maclic_plus_kg', 'napier_hay_silage_kg',
            'total_concentrate_kg', 'total_mineral_kg', 'total_feed_kg',
            'recorded_by', 'notes', 'created_at', 'updated_at'
        ]

class ChickenFeedConsumptionSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.batch_name', read_only=True)
    cost_per_bird = serializers.ReadOnlyField()
    
    class Meta:
        model = ChickenFeedConsumption
        fields = [
            'id', 'batch', 'batch_name', 'date', 'feed_quantity_kg',
            'feed_cost', 'cost_per_bird', 'recorded_by', 'notes',
            'created_at', 'updated_at'
        ]

class FeedInventorySerializer(serializers.ModelSerializer):
    feed_type_name = serializers.CharField(source='feed_type.name', read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()
    
    class Meta:
        model = FeedInventory
        fields = [
            'id', 'farm', 'feed_type', 'feed_type_name', 'current_stock',
            'minimum_stock_level', 'is_low_stock', 'stock_status',
            'last_updated', 'created_at', 'updated_at'
        ]