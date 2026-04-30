from django.contrib import admin
from .models import MpesaTransaction, ExpenseCategory


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'transaction_type', 'amount', 'status', 'purpose', 'mpesa_receipt', 'created_at']
    list_filter = ['transaction_type', 'status', 'purpose', 'is_expense']
    search_fields = ['farmer__username', 'mpesa_receipt', 'phone_number']
    date_hierarchy = 'created_at'


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
