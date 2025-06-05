# apps/health/models.py
from django.db import models
from django.core.validators import MinValueValidator
from apps.common.models import BaseModel

class Veterinarian(BaseModel):
    """Veterinarian contact information"""
    
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'health_veterinarians'
        verbose_name = 'Veterinarian'
        verbose_name_plural = 'Veterinarians'
        ordering = ['name']
    
    def __str__(self):
        return f"Dr. {self.name} ({self.license_number})"

class HealthRecord(BaseModel):
    """Health records for cows - only accessible to admins"""
    
    ANIMAL_TYPE_CHOICES = [
        ('cow', 'Cow'),
        ('chicken_batch', 'Chicken Batch'),
    ]
    
    TREATMENT_STATUS_CHOICES = [
        ('diagnosed', 'Diagnosed'),
        ('treating', 'Under Treatment'),
        ('recovered', 'Recovered'),
        ('chronic', 'Chronic'),
        ('dead', 'Dead'),
    ]
    
    # Animal reference (polymorphic relationship)
    animal_type = models.CharField(max_length=15, choices=ANIMAL_TYPE_CHOICES)
    cow = models.ForeignKey(
        'livestock.Cow',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='health_records'
    )
    chicken_batch = models.ForeignKey(
        'livestock.ChickenBatch',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='health_records'
    )
    
    # Health record details
    date_reported = models.DateField()
    disease_name = models.CharField(max_length=100)
    symptoms = models.TextField()
    diagnosis = models.TextField(blank=True, null=True)
    treatment_date = models.DateField(null=True, blank=True)
    medicine_used = models.TextField(blank=True, null=True)
    medicine_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    veterinarian = models.ForeignKey(
        Veterinarian,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='treatments'
    )
    treatment_status = models.CharField(
        max_length=15,
        choices=TREATMENT_STATUS_CHOICES,
        default='diagnosed'
    )
    recovery_date = models.DateField(null=True, blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'health_records'
        verbose_name = 'Health Record'
        verbose_name_plural = 'Health Records'
        ordering = ['-date_reported']
    
    def __str__(self):
        animal_name = self.cow.name if self.cow else self.chicken_batch.batch_name
        return f"{animal_name} - {self.disease_name} ({self.date_reported})"
    
    @property
    def farm(self):
        if self.cow:
            return self.cow.farm
        elif self.chicken_batch:
            return self.chicken_batch.farm
        return None
    
    @property
    def animal_name(self):
        if self.cow:
            return self.cow.name
        elif self.chicken_batch:
            return self.chicken_batch.batch_name
        return "Unknown"