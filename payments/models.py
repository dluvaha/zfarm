from django.db import models
from django.conf import settings
import uuid


class MpesaTransaction(models.Model):
    """M-Pesa payment transaction records"""
    TRANSACTION_TYPES = [
        ('stk_push', 'STK Push (Pay)'),
        ('c2b', 'Customer to Business'),
        ('b2c', 'Business to Customer'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    PURPOSE_CHOICES = [
        ('vet_services', 'Veterinary Services'),
        ('feed', 'Animal Feed'),
        ('medicine', 'Medicine'),
        ('transport', 'Transport'),
        ('animal_purchase', 'Animal Purchase'),
        ('animal_sale', 'Animal Sale'),
        ('product_sale', 'Product Sale (Milk/Eggs)'),
        ('equipment', 'Equipment'),
        ('labour', 'Labour'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mpesa_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='stk_push')
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, blank=True)
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    mpesa_receipt = models.CharField(max_length=50, blank=True, help_text="M-Pesa confirmation code")
    checkout_request_id = models.CharField(max_length=100, blank=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, blank=True, help_text="Reference to related record (animal, health record, etc.)")
    is_expense = models.BooleanField(default=True, help_text="True = expense, False = income")
    result_code = models.CharField(max_length=10, blank=True)
    result_desc = models.TextField(blank=True)
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'M-Pesa Transaction'
        verbose_name_plural = 'M-Pesa Transactions'

    def __str__(self):
        return f"{self.mpesa_receipt or 'Pending'} - KES {self.amount} ({self.status})"


class ExpenseCategory(models.Model):
    """Categories for farm expenses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='💰')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
