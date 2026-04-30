from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class Farmer(AbstractUser):
    """Custom user model for livestock farmers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    mpesa_number = models.CharField(max_length=20, blank=True, null=True, help_text="M-Pesa linked phone number")
    id_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    county = models.CharField(max_length=100, blank=True)
    farm_type = models.CharField(max_length=100, blank=True, help_text="e.g., Dairy, Poultry, Mixed")
    farm_name = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_vet = models.BooleanField(default=False, help_text="Is this user a veterinarian?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Farmer'
        verbose_name_plural = 'Farmers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.username} - {self.farm_name or 'No Farm'}"

    @property
    def total_animals(self):
        return self.farms.aggregate(total=models.Count('animals'))['total'] or 0

    @property
    def has_farm(self):
        return self.farms.exists()


class OTPVerification(models.Model):
    """OTP for phone number verification"""
    phone_number = models.CharField(max_length=20)
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.phone_number}"


class Farm(models.Model):
    """Farm profile linked to a farmer"""
    LIVESTOCK_TYPES = [
        ('cattle', 'Cattle'),
        ('goats', 'Goats'),
        ('sheep', 'Sheep'),
        ('poultry', 'Poultry'),
        ('pigs', 'Pigs'),
        ('rabbits', 'Rabbits'),
        ('mixed', 'Mixed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    county = models.CharField(max_length=100, blank=True)
    size_acres = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    livestock_type = models.CharField(max_length=20, choices=LIVESTOCK_TYPES, default='mixed')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Farm'
        verbose_name_plural = 'Farms'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.owner.get_full_name() or self.owner.username}"

    @property
    def animal_count(self):
        return self.animals.count()

    @property
    def active_listings(self):
        return self.marketplace_listings.filter(status='active').count()
