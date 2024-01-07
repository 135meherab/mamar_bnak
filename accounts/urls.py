from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
urlpatterns = [
    path('register/', views.UserSignupView.as_view(), name='signup_page'),
    path('login/', views.UserLogin.as_view(), name='login_page'),
    path('logout/', views.UserLogout.as_view(), name='logout_page'),
]