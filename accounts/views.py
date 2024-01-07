from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms  import SignUpForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
# Create your views here.

def send_transaction_mail(user, subject,template):
    mail_subject = subject
    mail_message = render_to_string(template,{
        'user': user,
    })
    send_mail = EmailMultiAlternatives(mail_subject,'',to = [user.email])
    send_mail.attach_alternative(mail_message, 'text/html')
    send_mail.send()

class UserSignupView(FormView):
    template_name ='accounts/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('signup_page')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    
class UserLogin(LoginView):
    template_name = 'accounts/login.html'
    def get_success_url(self):
        return reverse_lazy('home_page')
    
class UserLogout(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home_page')

def UpdatePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            send_transaction_mail(request.user, 'Your password has been changed', 'accounts/change_password_mail.html')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
