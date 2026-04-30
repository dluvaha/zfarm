from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Farmer, Farm


class FarmerRegistrationForm(UserCreationForm):
    """Registration form for farmers"""
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g., +254712345678'
        })
    )
    mpesa_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'M-Pesa linked number (optional)'
        })
    )
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g., Nakuru, Kenya'
        })
    )
    farm_type = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g., Dairy, Poultry, Mixed'
        })
    )

    class Meta:
        model = Farmer
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'mpesa_number', 'location', 'farm_type', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.attrs.get('class'):
                continue
            field.widget.attrs.update({'class': 'form-input'})

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if Farmer.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone


class FarmerLoginForm(AuthenticationForm):
    """Login form for farmers"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


class FarmerProfileForm(forms.ModelForm):
    """Form to update farmer profile"""
    class Meta:
        model = Farmer
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'mpesa_number', 'location', 'county', 'farm_type', 'farm_name', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'mpesa_number': forms.TextInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'county': forms.TextInput(attrs={'class': 'form-input'}),
            'farm_type': forms.TextInput(attrs={'class': 'form-input'}),
            'farm_name': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not field.widget.attrs.get('class'):
                field.widget.attrs.update({'class': 'form-input'})


class FarmForm(forms.ModelForm):
    """Form to create/update a farm"""
    class Meta:
        model = Farm
        fields = ['name', 'location', 'county', 'size_acres', 'livestock_type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Farm name'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 2km from Nakuru town'}),
            'county': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'County'}),
            'size_acres': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Size in acres'}),
            'livestock_type': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Brief description of your farm'}),
        }
