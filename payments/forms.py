from django import forms
from .models import MpesaTransaction


class MpesaPaymentForm(forms.Form):
    """Form to initiate M-Pesa STK Push payment"""
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g., 254712345678'
        })
    )
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Amount in KES',
            'min': '1',
            'step': '0.01'
        })
    )
    purpose = forms.ChoiceField(
        choices=MpesaTransaction.PURPOSE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Payment description (optional)'
        })
    )
    is_expense = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    reference_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )


class TransactionSearchForm(forms.Form):
    """Form to search/filter transactions"""
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    transaction_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(MpesaTransaction.TRANSACTION_TYPES),
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + list(MpesaTransaction.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    purpose = forms.ChoiceField(
        required=False,
        choices=[('', 'All Purposes')] + list(MpesaTransaction.PURPOSE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-input'})
    )
