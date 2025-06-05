# apps/breeding/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from apps.common.models import BaseModel

class BreedingRecord(BaseModel):
    """Breeding cycle management for cows"""
    
    BREEDING_METHOD_CHOICES = [
        ('ai', 'Artificial Insemination'),
        ('natural', 'Natural Breeding'),
    ]
    
    cow = models.ForeignKey(
        'livestock.Cow',
        on_delete=models.CASCADE,
        related_name='breeding_records'
    )
    breeding_date = models.DateField()
    breeding_method = models.CharField(
        max_length=10,
        choices=BREEDING_METHOD_CHOICES,
        default='ai'
    )
    bull_info = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Bull name/ID or AI straw details"
    )
    ai_technician = models.CharField(max_length=100, blank=True, null=True)
    breeding_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    heat_detected_date = models.DateField()
    expected_calving_date = models.DateField()
    pregnancy_confirmed = models.BooleanField(default=False)
    pregnancy_test_date = models.DateField(null=True, blank=True)
    actual_calving_date = models.DateField(null=True, blank=True)
    calving_complications = models.TextField(blank=True, null=True)
    calf_born = models.ForeignKey(
        'livestock.Cow',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='birth_record'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'breeding_records'
        verbose_name = 'Breeding Record'
        verbose_name_plural = 'Breeding Records'
        ordering = ['-breeding_date']
    
    def __str__(self):
        return f"{self.cow.name} - Bred on {self.breeding_date}"
    
    @property
    def farm(self):
        return self.cow.farm
    
    @property
    def gestation_period_days(self):
        if self.actual_calving_date:
            return (self.actual_calving_date - self.breeding_date).days
        return None
    
    @property
    def is_overdue(self):
        if not self.pregnancy_confirmed or self.actual_calving_date:
            return False
        return timezone.now().date() > self.expected_calving_date
    
    @property
    def days_to_calving(self):
        if self.actual_calving_date or not self.pregnancy_confirmed:
            return None
        return (self.expected_calving_date - timezone.now().date()).days
    
    def save(self, *args, **kwargs):
        # Auto-calculate expected calving date (283 days from breeding)
        if not self.expected_calving_date:
            self.expected_calving_date = self.breeding_date + timedelta(days=283)
        super().save(*args, **kwargs)

class HeatDetection(BaseModel):
    """Track heat detection in cows"""
    
    cow = models.ForeignKey(
        'livestock.Cow',
        on_delete=models.CASCADE,
        related_name='heat_detections'
    )
    heat_date = models.DateField()
    heat_intensity = models.CharField(
        max_length=10,
        choices=[
            ('weak', 'Weak'),
            ('moderate', 'Moderate'),
            ('strong', 'Strong'),
        ],
        default='moderate'
    )
    bred_this_cycle = models.BooleanField(default=False)
    breeding_record = models.ForeignKey(
        BreedingRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='heat_detection'
    )
    detected_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='heat_detections'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'breeding_heat_detections'
        verbose_name = 'Heat Detection'
        verbose_name_plural = 'Heat Detections'
        ordering = ['-heat_date']
    
    def __str__(self):
        return f"{self.cow.name} - Heat detected on {self.heat_date}"
    
    @property
    def farm(self):
        return self.cow.farm

