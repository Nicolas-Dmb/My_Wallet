from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import datetime
from django.conf import settings

'''
- Tester de créer un user avec et sans les blank True
- Tester de créer un user avec deux fois la même Username/Email/Phone
- Configurer les settings en faisant une erreur dans CurrencyList
- Configurer les settings en faisant une erreur dans Colors 
- Configurer normalement le setting 
- Se connecter 
- refresh 
'''

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True, blank=False)
    country = models.CharField(max_length=100, blank=True)
    job = models.CharField(max_length=100, blank=True)
    income = models.CharField(max_length=100, blank=True)
    birthday = models.DateField(blank=True, null=True)
    date_joined = models.DateTimeField(default=datetime.now)
    email_verif = models.BooleanField(default=False)

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
    


