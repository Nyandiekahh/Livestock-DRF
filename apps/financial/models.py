# apps/financial/models.py
from django.db import models
from django.core.validators import MinValueValidator
from apps.common.models import BaseModel

class Transaction(BaseModel):
    """General financial transaction model"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    CATEGORY_CHOICES = [
        ('milk_sales', 'Milk Sales'),
        ('livestock_sales', 'Livestock Sales'),
        ('egg_sales', 'Egg Sales'),
        ('feed_purchase', 'Feed Purchase'),
        ('veterinary', 'Veterinary Services'),
        ('breeding', 'Breeding Costs'),
        ('equipment', 'Equipment'),
        ('labor', 'Labor'),
        ('utilities', 'Utilities'),
        ('transport', 'Transport'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('mobile', 'Mobile Money'),
        ('check', 'Check'),
        ('credit', 'Credit'),
    ]
    
    farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField()
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    description = models.TextField()
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Reference to related records
    milk_sale = models.ForeignKey(
        'production.MilkSale',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transactions'
    )
    feed_purchase = models.ForeignKey(
        'feeds.FeedPurchase',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transactions'
    )
    health_record = models.ForeignKey(
        'health.HealthRecord',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transactions'
    )
    breeding_record = models.ForeignKey(
        'breeding.BreedingRecord',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    recorded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='financial_transactions'
    )
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'financial_transactions'
        verbose_name = 'Financial Transaction'
        verbose_name_plural = 'Financial Transactions'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.farm.name} - {self.get_transaction_type_display()}: {self.amount} ({self.date})"

class MonthlyFinancialSummary(BaseModel):
    """Monthly financial summary per farm"""
    
    farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.CASCADE,
        related_name='monthly_summaries'
    )
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()  # 1-12
    
    # Income breakdown
    total_income = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    milk_sales_income = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    livestock_sales_income = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    egg_sales_income = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    other_income = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    
    # Expense breakdown
    total_expenses = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    feed_expenses = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    veterinary_expenses = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    breeding_expenses = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    labor_expenses = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    other_expenses = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    
    # Calculated fields
    net_profit = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    profit_margin = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    
    class Meta:
        db_table = 'financial_monthly_summaries'
        verbose_name = 'Monthly Financial Summary'
        verbose_name_plural = 'Monthly Financial Summaries'
        unique_together = ['farm', 'year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.farm.name} - {self.year}/{self.month:02d}"
    
    def calculate_summary(self):
        """Calculate monthly summary from transactions"""
        from django.db.models import Sum, Q
        
        transactions = Transaction.objects.filter(
            farm=self.farm,
            date__year=self.year,
            date__month=self.month,
            is_deleted=False
        )
        
        # Calculate income
        income_transactions = transactions.filter(transaction_type='income')
        self.total_income = income_transactions.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        self.milk_sales_income = income_transactions.filter(
            category='milk_sales'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        self.livestock_sales_income = income_transactions.filter(
            category='livestock_sales'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        self.egg_sales_income = income_transactions.filter(
            category='egg_sales'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate expenses
        expense_transactions = transactions.filter(transaction_type='expense')
        self.total_expenses = expense_transactions.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        self.feed_expenses = expense_transactions.filter(
            category='feed_purchase'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        self.veterinary_expenses = expense_transactions.filter(
            category='veterinary'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        self.breeding_expenses = expense_transactions.filter(
            category='breeding'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        self.labor_expenses = expense_transactions.filter(
            category='labor'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate net profit and margin
        self.net_profit = self.total_income - self.total_expenses
        if self.total_income > 0:
            self.profit_margin = (self.net_profit / self.total_income) * 100
        else:
            self.profit_margin = 0
        
        self.save()

