# apps/production/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.common.models import BaseModel

class MilkProduction(BaseModel):
    """Daily milk production tracking for individual cows"""
    
    MILKING_SESSION_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
    ]
    
    cow = models.ForeignKey(
        'livestock.Cow',
        on_delete=models.CASCADE,
        related_name='milk_productions'
    )
    date = models.DateField()
    session = models.CharField(max_length=10, choices=MILKING_SESSION_CHOICES)
    quantity_liters = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    quality_grade = models.CharField(
        max_length=1,
        choices=[('A', 'Grade A'), ('B', 'Grade B'), ('C', 'Grade C')],
        default='A'
    )
    recorded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='milk_records'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'production_milk'
        verbose_name = 'Milk Production'
        verbose_name_plural = 'Milk Production Records'
        ordering = ['-date', '-session']
        unique_together = ['cow', 'date', 'session']
    
    def __str__(self):
        return f"{self.cow.name} - {self.date} {self.session}: {self.quantity_liters}L"
    
    @property
    def farm(self):
        return self.cow.farm

class DailyMilkSummary(BaseModel):
    """Daily milk production summary per farm"""
    
    farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.CASCADE,
        related_name='daily_milk_summaries'
    )
    date = models.DateField()
    total_morning = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    total_afternoon = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    total_evening = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    total_daily = models.DecimalField(
        max_digits=8, decimal_places=2, default=0
    )
    cows_milked = models.PositiveIntegerField(default=0)
    average_per_cow = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )
    
    class Meta:
        db_table = 'production_daily_milk_summary'
        verbose_name = 'Daily Milk Summary'
        verbose_name_plural = 'Daily Milk Summaries'
        ordering = ['-date']
        unique_together = ['farm', 'date']
    
    def __str__(self):
        return f"{self.farm.name} - {self.date}: {self.total_daily}L"
    
    def calculate_summary(self):
        """Calculate and update summary from individual records"""
        from django.db.models import Sum, Count, Avg
        
        daily_records = MilkProduction.objects.filter(
            cow__farm=self.farm,
            date=self.date,
            is_deleted=False
        )
        
        # Calculate totals by session
        morning_total = daily_records.filter(session='morning').aggregate(
            total=Sum('quantity_liters')
        )['total'] or 0
        
        afternoon_total = daily_records.filter(session='afternoon').aggregate(
            total=Sum('quantity_liters')
        )['total'] or 0
        
        evening_total = daily_records.filter(session='evening').aggregate(
            total=Sum('quantity_liters')
        )['total'] or 0
        
        # Calculate other metrics
        unique_cows = daily_records.values('cow').distinct().count()
        total_daily = morning_total + afternoon_total + evening_total
        avg_per_cow = total_daily / unique_cows if unique_cows > 0 else 0
        
        # Update fields
        self.total_morning = morning_total
        self.total_afternoon = afternoon_total
        self.total_evening = evening_total
        self.total_daily = total_daily
        self.cows_milked = unique_cows
        self.average_per_cow = avg_per_cow
        self.save()

class MilkSale(BaseModel):
    """Milk sales tracking - only visible to admins"""
    
    farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.CASCADE,
        related_name='milk_sales'
    )
    date = models.DateField()
    quantity_liters = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    price_per_liter = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    buyer_name = models.CharField(max_length=100, blank=True, null=True)
    buyer_contact = models.CharField(max_length=15, blank=True, null=True)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Cash'),
            ('bank', 'Bank Transfer'),
            ('mobile', 'Mobile Money'),
            ('credit', 'Credit'),
        ],
        default='cash'
    )
    recorded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='milk_sales_recorded'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'production_milk_sales'
        verbose_name = 'Milk Sale'
        verbose_name_plural = 'Milk Sales'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.farm.name} - {self.date}: {self.quantity_liters}L @ {self.price_per_liter}/L"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount
        self.total_amount = self.quantity_liters * self.price_per_liter
        super().save(*args, **kwargs)

class EggProduction(BaseModel):
    """Daily egg production tracking for chicken batches"""
    
    batch = models.ForeignKey(
        'livestock.ChickenBatch',
        on_delete=models.CASCADE,
        related_name='egg_productions'
    )
    date = models.DateField()
    eggs_collected = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    broken_eggs = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    eggs_consumed = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    eggs_sold = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    recorded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='egg_records'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'production_eggs'
        verbose_name = 'Egg Production'
        verbose_name_plural = 'Egg Production Records'
        ordering = ['-date']
        unique_together = ['batch', 'date']
    
    def __str__(self):
        return f"{self.batch.batch_name} - {self.date}: {self.eggs_collected} eggs"
    
    @property
    def farm(self):
        return self.batch.farm
    
    @property
    def usable_eggs(self):
        return self.eggs_collected - self.broken_eggs

class ChickHatching(BaseModel):
    """Track chick hatching events"""
    
    batch = models.ForeignKey(
        'livestock.ChickenBatch',
        on_delete=models.CASCADE,
        related_name='hatchings'
    )
    date = models.DateField()
    eggs_set_for_hatching = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    chicks_hatched = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    failed_eggs = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    recorded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='hatching_records'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'production_chick_hatching'
        verbose_name = 'Chick Hatching'
        verbose_name_plural = 'Chick Hatching Records'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.batch.batch_name} - {self.date}: {self.chicks_hatched} chicks hatched"
    
    @property
    def farm(self):
        return self.batch.farm
    
    @property
    def hatching_rate(self):
        if self.eggs_set_for_hatching > 0:
            return (self.chicks_hatched / self.eggs_set_for_hatching) * 100
        return 0
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Automatically add hatched chicks to the batch
        self.batch.add_hatched_chicks(self.chicks_hatched)