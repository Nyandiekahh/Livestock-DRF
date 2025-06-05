# apps/health/admin.py
from django.contrib import admin
from .models import Veterinarian, HealthRecord

@admin.register(Veterinarian)
class VeterinarianAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'license_number', 'phone_number', 'location',
        'specialization', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'location', 'specialization']
    search_fields = ['name', 'license_number', 'phone_number', 'email']
    ordering = ['name']

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = [
        'animal_name', 'animal_type', 'disease_name', 'date_reported',
        'treatment_status', 'veterinarian', 'medicine_cost'
    ]
    list_filter = [
        'animal_type', 'treatment_status', 'date_reported',
        'veterinarian', 'follow_up_required'
    ]
    search_fields = ['disease_name', 'symptoms', 'diagnosis', 'medicine_used']
    ordering = ['-date_reported']
    date_hierarchy = 'date_reported'
    
    fieldsets = (
        ('Animal Information', {
            'fields': ('animal_type', 'cow', 'chicken_batch')
        }),
        ('Health Issue', {
            'fields': ('date_reported', 'disease_name', 'symptoms', 'diagnosis')
        }),
        ('Treatment', {
            'fields': (
                'treatment_date', 'medicine_used', 'medicine_cost',
                'veterinarian', 'treatment_status'
            )
        }),
        ('Recovery and Follow-up', {
            'fields': (
                'recovery_date', 'follow_up_required', 'follow_up_date'
            )
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
    )
