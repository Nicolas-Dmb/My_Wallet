from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import datetime
from django.conf import settings
from django.db import transaction
from django.utils import timezone

def default_otp_time():
    return timezone.now() - timezone.timedelta(seconds=600)

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
    # dit si la vérif de l'otp est valide 
    otp_verif = models.DateTimeField(default=default_otp_time)
    # ces deux valeurs permettent de vérifier l'otp retourné par l'user et si toujours valide
    otp_key = models.IntegerField(blank=True, null=True)
    otp_generate = models.DateTimeField(default=default_otp_time) # détermine la limite pour taper le code à seconds=60) ici c'est juste la date de génération
    #MP Oublié
    token = models.CharField(max_length=200, blank=True, null=True)
    date_token = models.DateTimeField(blank=True, null=True)

    @transaction.atomic
    def OTP_Set(self):
        self.otp_verif = timezone.now() + timezone.timedelta(seconds=600)
        self.save()

    @transaction.atomic
    def OTP_Status(self):
        if self.otp_verif > timezone.now():
            return True
        return False

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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    


