from django import forms
from maps.models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        # CHÈN THÊM 'short_description' VÀO DANH SÁCH NÀY:
        fields = ['title', 'short_description', 'content', 'date', 'is_active', 'image']
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }