from django.db import models
from django.conf import settings
import uuid


class MarketplaceListing(models.Model):
    """Animals or products listed for sale in the marketplace"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    CATEGORY_CHOICES = [
        ('animal', 'Live Animal'),
        ('milk', 'Milk'),
        ('eggs', 'Eggs'),
        ('feed', 'Animal Feed'),
        ('equipment', 'Farm Equipment'),
        ('other', 'Other Products'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marketplace_listings')
    farm = models.ForeignKey('accounts.Farm', on_delete=models.CASCADE, related_name='marketplace_listings', null=True, blank=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='animal')
    animal = models.ForeignKey('animals.Animal', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(help_text="Describe the animal/product, health status, breed, age, etc.")
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in KES")
    negotiable = models.BooleanField(default=True)
    location = models.CharField(max_length=200)
    county = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    image = models.ImageField(upload_to='marketplace/', blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Marketplace Listing'
        verbose_name_plural = 'Marketplace Listings'

    def __str__(self):
        return f"{self.title} - KES {self.price} ({self.status})"


class BuyerInquiry(models.Model):
    """Buyer inquiries/messages for marketplace listings"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('responded', 'Responded'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(MarketplaceListing, on_delete=models.CASCADE, related_name='inquiries')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_inquiries')
    message = models.TextField(help_text="Buyer's inquiry message")
    offer_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Buyer's proposed price")
    phone_number = models.CharField(max_length=20, help_text="Buyer's phone number for contact")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    seller_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry on '{self.listing.title}' by {self.buyer.username}"
