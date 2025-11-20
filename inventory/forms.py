from django import forms
from .models import BorrowRecord

class BorrowForm(forms.ModelForm): # [cite: 24]
    class Meta:
        model = BorrowRecord
        fields = [] # We don't need fields, we just need the button to confirm borrowing