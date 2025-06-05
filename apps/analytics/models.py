# apps/analytics/models.py
from django.db import models
from apps.common.models import BaseModel

class ProductionReport(BaseModel):
    """Generated production reports"""
    
    REPORT_TYPE_CHOICES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('yearly', 'Yearly Report'),
        ('custom', 'Custom Period Report'),
    ]
    
    farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.CASCADE,
        related_name='production_reports'
    )
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    report_data = models.JSONField()  # Store calculated statistics
    generated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports'
    )
    file_path = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'analytics_production_reports'
        verbose_name = 'Production Report'
        verbose_name_plural = 'Production Reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.farm.name} - {self.get_report_type_display()} ({self.start_date} to {self.end_date})"