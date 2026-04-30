from django.db import models
from django.conf import settings
import uuid


class Notification(models.Model):
    """User notifications for alerts, reminders, and confirmations"""
    TYPE_CHOICES = [
        ('feeding', 'Feeding Reminder'),
        ('vet', 'Vet Appointment'),
        ('vaccination', 'Vaccination Due'),
        ('payment', 'Payment Confirmation'),
        ('marketplace', 'Marketplace Update'),
        ('health', 'Health Alert'),
        ('system', 'System Notification'),
        ('production', 'Production Alert'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    related_id = models.CharField(max_length=100, blank=True)
    related_model = models.CharField(max_length=50, blank=True)
    action_url = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.farmer.username}"

    @classmethod
    def create_notification(cls, farmer, title, message, notification_type='system',
                            related_id='', related_model='', action_url=''):
        return cls.objects.create(
            farmer=farmer, title=title, message=message,
            notification_type=notification_type, related_id=str(related_id),
            related_model=related_model, action_url=action_url,
        )


class FeedingSchedule(models.Model):
    """Feeding schedules for animals/herds"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('twice_daily', 'Twice Daily'),
        ('weekly', 'Weekly'),
        ('custom', 'Custom'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey('accounts.Farm', on_delete=models.CASCADE, related_name='feeding_schedules')
    animal = models.ForeignKey('animals.Animal', on_delete=models.CASCADE, null=True, blank=True)
    feed_type = models.CharField(max_length=200)
    quantity = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    time = models.TimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['time']

    def __str__(self):
        animal_str = f" - {self.animal.tag_id}" if self.animal else " (All)"
        return f"{self.feed_type}{animal_str} - {self.frequency}"
