from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import datetime
from django.conf import settings
from django.db import transaction
from django.utils import timezone

'''
- Tester de créer un user avec et sans les blank True
- Tester de créer un user avec deux fois la même Username/Email/Phone
- Configurer les settings en faisant une erreur dans CurrencyList
- Configurer les settings en faisant une erreur dans Colors 
- Configurer normalement le setting 
- Se connecter 
- refresh 
- on véirife que les OTP Set et OTP Status fonctionne bien. 
'''

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,unique=True)
    phone = models.CharField(max_length=20, unique=True, blank=False)
    country = models.CharField(max_length=100, blank=True)
    job = models.CharField(max_length=100, blank=True)
    income = models.CharField(max_length=100, blank=True)
    birthday = models.DateField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)


    email_verif = models.BooleanField(default=False)
    phone_verif = models.BooleanField(default=False)
    otp_verif = models.DateTimeField(default=timezone.datetime(2000, 1, 1, 1, 1, 1))
    otp_key = models.IntegerField(blank=True)
    otp_generate = models.DateTimeField(default=timezone.datetime(2000, 1, 1, 1, 1, 1))

    @transaction.atomic
    def OTP_Set(self):
        self.otp_verif = timezone.now() + timezone.timedelta(seconds=600)
        self.save()

    @transaction.atomic
    def OTP_Status(self):
        if self.otp_verif > timezone.now:
            return False
        return True

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username
    
class Setting(models.Model):
    class CurrencyList(models.TextChoices): 
        Euro = 'Euro', 
        Dollar = 'Dollar',
    
    class Colors(models.TextChoices): 
        Gray = 'Gray', 
        Red = 'Red', 
        Pink = 'Pink', 
        Purple = 'Purple', 
        Blue = 'Blue', 
        Green = 'Green', 
        Brown = 'Brown', 
        Yellow = 'Yellow', 
    
    currency = models.CharField(max_length=10, default=CurrencyList.Euro, choices=CurrencyList.choices, blank=False)
    nightMode = models.BooleanField(default=True, blank=False)
    color = models.CharField(max_length=20, default=Colors.Red, choices=Colors.choices, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    


