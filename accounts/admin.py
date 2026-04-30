from django.contrib import admin
from .models import Farmer, OTPVerification, Farm


@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'farm_name', 'location', 'is_verified', 'is_vet', 'created_at']
    list_filter = ['is_verified', 'is_vet', 'county', 'farm_type']
    search_fields = ['username', 'email', 'phone_number', 'farm_name']
    date_hierarchy = 'created_at'


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'otp_code', 'is_used', 'created_at']


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'location', 'county', 'livestock_type', 'size_acres', 'is_active', 'created_at']
    list_filter = ['livestock_type', 'is_active', 'county']
    search_fields = ['name', 'owner__username', 'location']
