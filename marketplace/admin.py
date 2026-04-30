from django.contrib import admin
from .models import MarketplaceListing, BuyerInquiry


@admin.register(MarketplaceListing)
class MarketplaceListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'price', 'status', 'location', 'views_count', 'created_at']
    list_filter = ['status', 'category', 'county']
    search_fields = ['title', 'description', 'seller__username']


@admin.register(BuyerInquiry)
class BuyerInquiryAdmin(admin.ModelAdmin):
    list_display = ['listing', 'buyer', 'phone_number', 'offer_price', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['buyer__username', 'message']
