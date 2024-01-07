from django.db import models

# Create your models here.
class BankRupt(models.Model):
    Bankrupt = models.BooleanField(default=False)
    bankrupt_time = models.DateTimeField(auto_now_add=True, blank=True, null = True)