# apps/feeds/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.common.models import BaseModel

class FeedType(BaseModel):
    """Different types of feeds available"""
    
    CATEGORY_CHOICES = [
        ('concentrate', 'Concentrate'),
        ('mineral', 'Mineral'),
        ('roughage', 'Roughage'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    unit_of_measurement = models.CharField(
        max_length=10,
        choices=[
            ('kg', 'Kilograms'),
            ('bags', 'Bags'),
            ('tonnes', 'Tonnes'),
            ('bales', 'Bales'),
        ],
        default='kg'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'feeds_types'
        verbose_name = 'Feed Type'
        verbose_name_plural = 'Feed Types'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class FeedPurchase(BaseModel):
    """Feed purchase records - only accessible to admins"""
    
    farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.CASCADE,
        related_name='feed_purchases'
    )
    feed_type = models.ForeignKey(
        FeedType,
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    purchase_date = models.DateField()
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    transport_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    supplier_name = models.CharField(max_length=100)
    supplier_contact = models.CharField(max_length=15, blank=True, null=True)
    remaining_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_finished = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    recorded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='feed_purchases_recorded'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'feeds_purchases'
        verbose_name = 'Feed Purchase'
        verbose_name_plural = 'Feed Purchases'
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"{self.feed_type.name} - {self.quantity}{self.feed_type.unit_of_measurement} on {self.purchase_date}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total cost if not provided
        if not self.total_cost:
            self.total_cost = self.quantity * self.unit_price
        
        # Set remaining quantity to purchased quantity if new record
        if not self.pk:
            self.remaining_quantity = self.quantity
        
        super().save(*args, **kwargs)
    
    def mark_as_finished(self):
        """Mark feed purchase as finished/restocked"""
        self.is_finished = True
        self.remaining_quantity = 0
        self.save()
    
    @property
    def consumption_percentage(self):
        if self.quantity > 0:
            consumed = self.quantity - self.remaining_quantity
            return (consumed / self.quantity) * 100
        return 0

class DailyFeedConsumption(BaseModel):
    """Daily feed consumption per cow"""
    
    cow = models.ForeignKey(
        'livestock.Cow',
        on_delete=models.CASCADE,
        related_name='feed_consumptions'
    )
    date = models.DateField()
    
    # Concentrates
    dairy_meal_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    maize_germ_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Minerals
    maclic_supa_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    maclic_plus_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Roughage (combined field as requested)
    napier_hay_silage_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    recorded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='feed_consumption_records'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'feeds_daily_consumption'
        verbose_name = 'Daily Feed Consumption'
        verbose_name_plural = 'Daily Feed Consumption Records'
        ordering = ['-date', 'cow__name']
        unique_together = ['cow', 'date']
    
    def __str__(self):
        return f"{self.cow.name} - {self.date} feed consumption"
    
    @property
    def farm(self):
        return self.cow.farm
    
    @property
    def total_concentrate_kg(self):
        return self.dairy_meal_kg + self.maize_germ_kg
    
    @property
    def total_mineral_kg(self):
        return self.maclic_supa_kg + self.maclic_plus_kg
    
    @property
    def total_feed_kg(self):
        return (
            self.total_concentrate_kg + 
            self.total_mineral_kg + 
            self.napier_hay_silage_kg
        )

class ChickenFeedConsumption(BaseModel):
    """Daily feed consumption for chicken batches"""
    
    batch = models.ForeignKey(
        'livestock.ChickenBatch',
        on_delete=models.CASCADE,
        related_name='feed_consumptions'
    )
    date = models.DateField()
    feed_quantity_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    feed_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    recorded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='chicken_feed_records'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'feeds_chicken_consumption'
        verbose_name = 'Chicken Feed Consumption'
        verbose_name_plural = 'Chicken Feed Consumption Records'
        ordering = ['-date']
        unique_together = ['batch', 'date']
    
    def __str__(self):
        return f"{self.batch.batch_name} - {self.date}: {self.feed_quantity_kg}kg"
    
    @property
    def farm(self):
        return self.batch.farm
    
    @property
    def cost_per_bird(self):
        if self.batch.current_count > 0:
            return self.feed_cost / self.batch.current_count
        return 0

class FeedInventory(BaseModel):
    """Track current feed inventory levels"""
    
    farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.CASCADE,
        related_name='feed_inventories'
    )
    feed_type = models.ForeignKey(
        FeedType,
        on_delete=models.CASCADE,
        related_name='inventories'
    )
    current_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    minimum_stock_level = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'feeds_inventory'
        verbose_name = 'Feed Inventory'
        verbose_name_plural = 'Feed Inventories'
        unique_together = ['farm', 'feed_type']
        ordering = ['farm', 'feed_type__category', 'feed_type__name']
    
    def __str__(self):
        return f"{self.farm.name} - {self.feed_type.name}: {self.current_stock}"
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock_level
    
    @property
    def stock_status(self):
        if self.is_low_stock:
            return "Low Stock"
        elif self.current_stock <= (self.minimum_stock_level * 1.5):
            return "Running Low"
        else:
            return "Good Stock"