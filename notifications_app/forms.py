from django import forms
from .models import FeedingSchedule


class FeedingScheduleForm(forms.ModelForm):
    class Meta:
        model = FeedingSchedule
        fields = ['animal', 'feed_type', 'quantity', 'frequency', 'time', 'notes']
        widgets = {
            'animal': forms.Select(attrs={'class': 'form-input'}),
            'feed_type': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Dairy Meal, Hay, Pellets'}),
            'quantity': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 5kg, 2 litres'}),
            'frequency': forms.Select(attrs={'class': 'form-input'}),
            'time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }
