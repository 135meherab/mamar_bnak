from django.db import models
from django.contrib.auth.models import User
from . constants import GENDERS, ACCOUNT_TYPES

# Create your models here.
class UserBankAccount(models.Model):
    user = models.OneToOneField(User, related_name="account", on_delete = models.CASCADE)
    account_type = models.CharField(max_length=25, choices = ACCOUNT_TYPES)
    account_no = models.IntegerField(unique=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices = GENDERS)
    acc_created_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    
    def __str__(self):
        return f'{str(self.account_no)} {self.user.username}'

class UserAddress(models.Model):
    user = models.OneToOneField(User, related_name="address", on_delete = models.CASCADE)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.user.email}'
    
