# apps/livestock/serializers.py
from rest_framework import serializers
from .models import Cow, ChickenBatch, ChickenReduction

class CowSerializer(serializers.ModelSerializer):
    age_in_months = serializers.ReadOnlyField()
    total_calves = serializers.ReadOnlyField()
    mother_name = serializers.CharField(source='mother.name', read_only=True)
    
    class Meta:
        model = Cow
        fields = [
            'id', 'farm', 'name', 'tag_number', 'breed', 'date_of_birth',
            'date_acquired', 'acquisition_cost', 'current_stage', 'weight',
            'mother', 'mother_name', 'father_info', 'image', 'notes',
            'is_active', 'age_in_months', 'total_calves', 'created_at', 'updated_at'
        ]

class CowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cow
        fields = [
            'farm', 'name', 'tag_number', 'breed', 'date_of_birth',
            'date_acquired', 'acquisition_cost', 'current_stage', 'weight',
            'mother', 'father_info', 'image', 'notes'
        ]

class ChickenBatchSerializer(serializers.ModelSerializer):
    mortality_count = serializers.ReadOnlyField()
    mortality_rate = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()
    
    class Meta:
        model = ChickenBatch
        fields = [
            'id', 'farm', 'batch_name', 'batch_type', 'initial_count',
            'current_count', 'date_acquired', 'acquisition_cost_per_bird',
            'expected_laying_start', 'notes', 'is_active', 'mortality_count',
            'mortality_rate', 'total_cost', 'created_at', 'updated_at'
        ]

class ChickenReductionSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.batch_name', read_only=True)
    
    class Meta:
        model = ChickenReduction
        fields = [
            'id', 'batch', 'batch_name', 'count', 'reason', 
            'date', 'notes', 'created_at'
        ]