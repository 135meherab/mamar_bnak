from typing import Any
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from .constants import ACCOUNT_TYPES, GENDERS
from . models import UserBankAccount, UserAddress

class SignUpForm(UserCreationForm):
    account_type = forms.ChoiceField(choices = ACCOUNT_TYPES)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices = GENDERS)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'birth_date','gender', 'email','account_type','street_address','city','postal_code','country']

    def save(self, commit=True):
        current_user = super().save(commit=False)
        if commit==True:
            current_user.save()
            birth_date = self.cleaned_data.get('birth_date')
            gender = self.cleaned_data.get('gender')
            account_type= self.cleaned_data.get('account_type')
            street_address = self.cleaned_data.get('street_address')
            city = self.cleaned_data.get('city')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')

            UserAddress.objects.create(
                user = current_user,
                street_address = street_address,
                city = city,
                postal_code = postal_code,
                country = country   
            )

            UserBankAccount.objects.create(
                user = current_user,
                account_type = account_type,
                birth_date = birth_date,
                gender = gender,
                account_no = 000000000 + current_user.id
            )
        
        return current_user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class' : (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
                })



class UpdateSignUpForm(forms.ModelForm):
    account_type = forms.ChoiceField(choices = ACCOUNT_TYPES)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices = GENDERS)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class' : (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )}
            )

        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address
            except:
                user_account = None
                user_address = None
        if user_account:
            self.fields['account_type'].initial = user_account.account_type
            self.fields['birth_date'].initial = user_account.birth_date
            self.fields['gender'].initial = user_account.gender
            self.fields['street_address'].initial = user_address.street_address
            self.fields['city'].initial = user_address.city
            self.fields['postal_code'].initial = user_address.postal_code
            self.fields['country'].initial = user_address.country
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user_account, created = UserBankAccount.objects.get_or_create(user=user)
            user_address, created = UserAddress.objects.get_or_create(user=user)
                
            user_account.account_type = self.cleaned_data.get('account_type')
            user_account.birth_date = self.cleaned_data.get('birth_date')
            user_account.gender = self.cleaned_data.get('gender')
            user_account.save()

            user_address.street_address = self.cleaned_data.get('street_address')
            user_address.city = self.cleaned_data.get('city')
            user_address.postal_code = self.cleaned_data.get('postal_code')
            user_address.country = self.cleaned_data.get('country')
            user_address.save()
            
        return user



