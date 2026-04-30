from django import forms
from .models import Animal, HealthRecord, ProductionRecord, AnimalMovement, Breed


class AnimalForm(forms.ModelForm):
    """Form to add/edit an animal"""
    class Meta:
        model = Animal
        fields = ['tag_id', 'name', 'category', 'breed', 'gender', 'date_of_birth', 'date_purchased', 'purchase_price', 'purchase_from', 'weight', 'color', 'status', 'notes', 'image']
        widgets = {
            'tag_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., TAG-001'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional friendly name'}),
            'category': forms.Select(attrs={'class': 'form-input', 'id': 'category-select'}),
            'breed': forms.Select(attrs={'class': 'form-input', 'id': 'breed-select'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_purchased': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'purchase_from': forms.TextInput(attrs={'class': 'form-input'}),
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'kg'}),
            'color': forms.TextInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        farm = kwargs.pop('farm', None)
        super().__init__(*args, **kwargs)
        if farm:
            self.instance.farm = farm


class HealthRecordForm(forms.ModelForm):
    """Form to add health records"""
    class Meta:
        model = HealthRecord
        fields = ['record_type', 'date', 'vet_name', 'diagnosis', 'treatment', 'medicine', 'cost', 'next_due_date', 'notes']
        widgets = {
            'record_type': forms.Select(attrs={'class': 'form-input'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'vet_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Veterinarian name'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'treatment': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'medicine': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Medicine name'}),
            'cost': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'next_due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }


class ProductionRecordForm(forms.ModelForm):
    """Form to add production records"""
    class Meta:
        model = ProductionRecord
        fields = ['record_type', 'date', 'quantity', 'notes']
        widgets = {
            'record_type': forms.Select(attrs={'class': 'form-input'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }


class AnimalMovementForm(forms.ModelForm):
    """Form to record animal movements"""
    class Meta:
        model = AnimalMovement
        fields = ['movement_type', 'date', 'from_location', 'to_location', 'price', 'notes']
        widgets = {
            'movement_type': forms.Select(attrs={'class': 'form-input'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'from_location': forms.TextInput(attrs={'class': 'form-input'}),
            'to_location': forms.TextInput(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }
