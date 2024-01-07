from django import forms
from .models import Transaction
from accounts.models import UserBankAccount

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type','amount']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit = True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()

class DepositForm(TransactionForm):
    def clean_amount(self):
        min_diposit = 100
        amount = self.cleaned_data.get('amount')
        if amount <= min_diposit:
            raise forms.ValidationError(f'You need to diposite at least {min_diposit}. TAKA')
        return amount
 
class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_withdraw = 500
        max_withdraw = 20000
        balance = account.balance
        amount = self.cleaned_data.get('amount')
        if amount > balance:
            raise forms.ValidationError(f'You don\'t have enough balance to withdraw. Your current balance is {balance} TAKA')
        if amount < min_withdraw:
            raise forms.ValidationError(f'You need to withdraw at least {min_withdraw} TAKA')
        if amount > max_withdraw:
            raise forms.ValidationError(f'You need to withdraw at most {max_withdraw} TAKA')
        return amount
    
class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        return amount


class TransferForm(forms.Form):
    account_no = forms.IntegerField()
    amount = forms.DecimalField()