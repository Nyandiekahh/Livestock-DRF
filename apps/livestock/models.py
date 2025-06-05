from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone  # Add this line
from apps.common.models import BaseModel

class Cow(BaseModel):
    """Individual cow management"""
    
    STAGE_CHOICES = [
        ('calf', 'Calf'),
        ('heifer', 'Heifer'),
        ('lactating', 'Lactating'),
        ('dry', 'Dry Period'),
        ('pregnant', 'Pregnant'),
        ('heat', 'In Heat'),
        ('sick', 'Sick'),
        ('sold', 'Sold'),
    ]
    
    BREED_CHOICES = [
        ('friesian', 'Friesian'),
        ('jersey', 'Jersey'),
        ('ayrshire', 'Ayrshire'),
        ('guernsey', 'Guernsey'),
        ('holstein', 'Holstein'),
        ('crossbreed', 'Crossbreed'),
        ('indigenous', 'Indigenous'),
    ]
    
    farm = models.ForeignKey(
        'farms.Farm', 
        on_delete=models.CASCADE, 
        related_name='cows'
    )
    name = models.CharField(max_length=50)
    tag_number = models.CharField(max_length=20, unique=True)
    breed = models.CharField(max_length=20, choices=BREED_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    date_acquired = models.DateField()
    acquisition_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    current_stage = models.CharField(max_length=15, choices=STAGE_CHOICES, default='heifer')
    weight = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    mother = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='calves'
    )
    father_info = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='cow_images/', null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'livestock_cows'
        verbose_name = 'Cow'
        verbose_name_plural = 'Cows'
        ordering = ['name']
        unique_together = ['farm', 'tag_number']
    
    def __str__(self):
        return f"{self.name} ({self.tag_number}) - {self.farm.name}"
    
    @property
    def age_in_months(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return (today.year - self.date_of_birth.year) * 12 + today.month - self.date_of_birth.month
        return None
    
    @property
    def is_milking(self):
        return self.current_stage == 'lactating'
    
    def total_calves(self):
        return self.calves.filter(is_deleted=False).count()

class ChickenBatch(BaseModel):
    """Chicken batch management - chickens handled as groups"""
    
    BATCH_TYPE_CHOICES = [
        ('layers', 'Layers'),
        ('broilers', 'Broilers'),
        ('mixed', 'Mixed'),
    ]
    
    farm = models.ForeignKey(
        'farms.Farm', 
        on_delete=models.CASCADE, 
        related_name='chicken_batches'
    )
    batch_name = models.CharField(max_length=50)
    batch_type = models.CharField(max_length=10, choices=BATCH_TYPE_CHOICES)
    initial_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    current_count = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    date_acquired = models.DateField()
    acquisition_cost_per_bird = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    expected_laying_start = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'livestock_chicken_batches'
        verbose_name = 'Chicken Batch'
        verbose_name_plural = 'Chicken Batches'
        ordering = ['-date_acquired']
        unique_together = ['farm', 'batch_name']
    
    def __str__(self):
        return f"{self.batch_name} ({self.current_count}/{self.initial_count}) - {self.farm.name}"
    
    @property
    def total_cost(self):
        return self.initial_count * self.acquisition_cost_per_bird
    
    @property
    def mortality_count(self):
        return self.initial_count - self.current_count
    
    @property
    def mortality_rate(self):
        if self.initial_count > 0:
            return (self.mortality_count / self.initial_count) * 100
        return 0
    
    def reduce_count(self, count, reason=""):
        """Reduce chicken count due to death, sale, etc."""
        if count <= self.current_count:
            self.current_count -= count
            self.save()
            
            # Log the reduction
            ChickenReduction.objects.create(
                batch=self,
                count=count,
                reason=reason,
                date=timezone.now().date()
            )
    
    def add_hatched_chicks(self, count):
        """Add newly hatched chicks to the batch"""
        self.current_count += count
        self.save()

class ChickenReduction(BaseModel):
    """Track chicken reductions (deaths, sales, etc.)"""
    
    REDUCTION_REASONS = [
        ('death', 'Death/Disease'),
        ('sale', 'Sale'),
        ('consumption', 'Consumption'),
        ('transfer', 'Transfer'),
        ('other', 'Other'),
    ]
    
    batch = models.ForeignKey(
        ChickenBatch, 
        on_delete=models.CASCADE, 
        related_name='reductions'
    )
    count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reason = models.CharField(max_length=15, choices=REDUCTION_REASONS)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'livestock_chicken_reductions'
        verbose_name = 'Chicken Reduction'
        verbose_name_plural = 'Chicken Reductions'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.batch.batch_name} - {self.count} {self.reason} on {self.date}"
