from django.urls import path
from .views import TransferMoneyView,DepositeMoneyView, WithdrawMoneyView, LoanRequestView, LoanListView, TransactionReportView, PayLoanView

urlpatterns = [
    path('diposite/', DepositeMoneyView.as_view(), name = 'deposite_money'),
    path('report/', TransactionReportView.as_view(), name = 'transaction_report'),
    path('withdraw/', WithdrawMoneyView.as_view(), name = 'withdraw_money'),
    path('laon_request/', LoanRequestView.as_view(), name = 'loan_request'),
    path('loans/', LoanListView.as_view(), name = 'loan_list'),
    path('transfer/', TransferMoneyView.as_view(), name = 'transfer'),
    path('loan/<int:loan_id>', PayLoanView.as_view(), name = 'pay_loan_view'),
]
