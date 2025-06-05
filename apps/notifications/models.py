# apps/notifications/models.py
from django.db import models
from apps.common.models import BaseModel

class Notification(BaseModel):
    """System notifications for users"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('low_stock', 'Low Stock Alert'),
        ('calving_due', 'Calving Due'),
        ('heat_detected', 'Heat Detected'),
        ('vaccination_due', 'Vaccination Due'),
        ('treatment_followup', 'Treatment Follow-up'),
        ('report_generated', 'Report Generated'),
        ('system', 'System Notification'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    recipient = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Optional references to related objects
    farm = models.ForeignKey(
        'farms.Farm',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    cow = models.ForeignKey(
        'livestock.Cow',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.get_full_name()} - {self.title}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()