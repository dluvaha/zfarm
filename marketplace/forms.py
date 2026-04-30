from django import forms
from .models import MarketplaceListing, BuyerInquiry


class ListingForm(forms.ModelForm):
    """Form to create/edit a marketplace listing"""
    class Meta:
        model = MarketplaceListing
        fields = ['title', 'category', 'animal', 'description', 'price', 'negotiable', 'location', 'county', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Freshian Heifer for Sale'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'animal': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Describe the item - breed, age, health status, weight, etc.'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Price in KES'}),
            'negotiable': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Nakuru Town'}),
            'county': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'County'}),
        }

    def __init__(self, *args, **kwargs):
        farm = kwargs.pop('farm', None)
        seller = kwargs.pop('seller', None)
        super().__init__(*args, **kwargs)
        if farm:
            self.instance.farm = farm
        if seller:
            self.instance.seller = seller


class BuyerInquiryForm(forms.ModelForm):
    """Form for buyers to make inquiries on listings"""
    class Meta:
        model = BuyerInquiry
        fields = ['message', 'offer_price', 'phone_number']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'I am interested in this listing. Please provide more details...'
            }),
            'offer_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': 'Your offer price (optional)'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your phone number (e.g., 254712345678)'
            }),
        }
