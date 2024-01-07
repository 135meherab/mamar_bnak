from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from . models import Transaction
from .forms import TransactionForm, DepositForm, WithdrawForm, LoanRequestForm, TransferForm
from .constants import DEPOSITE, WITHDRAW, LOAN, LOAN_PAID, TRANSFERED, RECEIVED
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from accounts.models import UserBankAccount
from bankrupt.models import BankRupt
from transactions.models import Transaction
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

# Create your views here.

def send_transaction_mail(user, amount, subject,template):
    mail_subject = subject
    mail_message = render_to_string(template,{
        'user': user,
        'amount': amount,

    })
    send_mail = EmailMultiAlternatives(mail_subject,'',to = [user.email])
    send_mail.attach_alternative(mail_message, 'text/html')
    send_mail.send()
        
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transactions_form.html'
    model = 'Transaction'
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account,
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title':self.title,
        })
        return context

class DepositeMoneyView(TransactionCreateMixin):
    form_class =  DepositForm
    title = 'Deposite Page'
    
    def get_initial(self):
        initial = {'transaction_type': DEPOSITE}
        return initial

    def form_valid(self, form):
        
        amount =  form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount 

        account.save(
            update_fields = ['balance']
        )
        messages.success(self.request, f'{amount} TAKA was successfully deposited')
        
        send_transaction_mail(self.request.user, amount, 'Deposite Mail','transactions/deposite_mail.html')    
        return super().form_valid(form)
    


class WithdrawMoneyView(TransactionCreateMixin):
    form_class =  WithdrawForm
    title = 'Withdraw Money'
    
    def get_initial(self):
        initial = {'transaction_type': WITHDRAW}
        return initial
    
    def form_valid(self, form):
        is_bankrupt = BankRupt.objects.first()

        if is_bankrupt.Bankrupt:
            messages.error(self.request, 'the bank is bankrupt.')
        else:
            amount =  form.cleaned_data.get('amount')
            account = self.request.user.account
            account.balance -= amount 

            account.save(
                update_fields = ['balance']
            )

            messages.success(self.request, f'{amount} TAKA was successfully withdrawd')
            send_transaction_mail(self.request.user, amount, 'Withdraw Mail','transactions/withdraw_mail.html')
        return super().form_valid(form)
    
class LoanRequestView(TransactionCreateMixin):
    form_class =  LoanRequestForm
    title = 'Loan Request Money'
    
    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial
    
    def form_valid(self, form):
        amount =  form.cleaned_data.get('amount')
        account = self.request.user.account
        loan_count = Transaction.objects.filter(account = account, transaction_type = 3, loan_approve = True ).count() 
        if loan_count >= 3:
            return HttpResponse('You have already tooked maximum time of loan')

        messages.success(self.request, f'Request for {amount} TAKA Loan submitted')
        send_transaction_mail(self.request.user, amount, 'Loan Request Mail','transactions/loan_request_mail.html')
        return super().form_valid(form)

class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(timestamp__date__gte = start_date, timestamp__date__lte = end_date)
            self.balance = Transaction.objects.filter(timestamp__date__gte = start_date, timestamp__date__lte = end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance

        is_bankrupt = BankRupt.objects.first()
        if is_bankrupt.Bankrupt:
            queryset = queryset.filter(timestamp__date__lt = is_bankrupt.bankrupt_time)

        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account':self.request.user.account,
        })
        return context


class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id = loan_id)

        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')

class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans'

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account = user_account, transaction_type = LOAN )
        return queryset
    

class TransferMoneyView(LoginRequiredMixin, View):
    template_name = 'transactions/transfer_money.html'
    
    def get(self, request):
        form = TransferForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = TransferForm(request.POST)
        if form.is_valid():
            to_account_no = form.cleaned_data['account_no']
            amount = form.cleaned_data['amount']
            is_account_exists = UserBankAccount.objects.filter(account_no=to_account_no).count()
            if is_account_exists > 0:
                destination_account = UserBankAccount.objects.get(account_no = to_account_no)
                destination_account.balance += amount
                destination_account.save()

                current_user_account = request.user.account
                current_user_account.balance -= amount
                current_user_account.save()

                Transaction.objects.create(
                    account = current_user_account,
                    amount = amount,
                    balance_after_transaction = current_user_account.balance,
                    transaction_type = TRANSFERED
                )

                Transaction.objects.create(
                    account = destination_account,
                    amount = amount,
                    balance_after_transaction = destination_account.balance,
                    transaction_type = RECEIVED
                )
                    
                messages.success(request,f'{amount} TAKA Successfully Transfer to {to_account_no}')

            else:
                messages.error(request, 'account does not exist')
            
            return render(request, self.template_name, {'form': form})
