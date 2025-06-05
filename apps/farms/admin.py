# apps/farms/admin.py
from django.contrib import admin
from .models import Farm

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'location', 'total_cows', 'total_chickens', 
        'active_farmers', 'is_active', 'created_at'
    ]
    list_filter = ['location', 'is_active', 'created_at']
    search_fields = ['name', 'location', 'address']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'address')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Additional Details', {
            'fields': ('established_date', 'description', 'is_active')
        }),
    )
