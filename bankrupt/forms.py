from . models import BankRupt
from django import forms
class BankRuptFrom(forms.ModelForm):
    class Meta:
        model = BankRupt
        fields = '__all__'