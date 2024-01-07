from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms  import SignUpForm
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView

# Create your views here.
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