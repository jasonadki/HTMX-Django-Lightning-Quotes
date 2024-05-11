from django import forms
from .models import Quote

class QuoteForm(forms.ModelForm):
    integer_field = forms.IntegerField(required=False, label='Your Integer')
    
    class Meta:
        model = Quote
        fields = ['content', 'integer_field']
