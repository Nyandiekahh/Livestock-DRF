# apps/farms/models.py
from django.db import models
from apps.common.models import BaseModel

class Farm(BaseModel):
    """Farm model representing each dairy farm location"""
    
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)  # e.g., "Nakuru", "Kisii"
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    established_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'farms'
        verbose_name = 'Farm'
        verbose_name_plural = 'Farms'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    @property
    def total_cows(self):
        return self.cows.filter(is_deleted=False).count()
    
    @property
    def total_chickens(self):
        return self.chicken_batches.filter(is_deleted=False).aggregate(
            total=models.Sum('current_count')
        )['total'] or 0
    
    @property
    def active_farmers(self):
        return self.farmers.filter(is_active=True).count()