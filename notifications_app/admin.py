from django.contrib import admin
from .models import Notification, FeedingSchedule


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['farmer__username', 'title']


@admin.register(FeedingSchedule)
class FeedingScheduleAdmin(admin.ModelAdmin):
    list_display = ['farm', 'animal', 'feed_type', 'quantity', 'frequency', 'time', 'is_active']
    list_filter = ['frequency', 'is_active']
