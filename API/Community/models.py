from django.db import models
from User.models import User
from django.conf import settings


'''
- Un user créer plus sujets.
- Deux user ont des Keywords similaires.
- deux user parlent dans un sujets similaires l'un envoie une photo et par l'autre.
- un User met un ou des sujets favoris. 
- un user recherche par keywords des sujets
'''
# Create your models here.
class Subject(models.Model):
    title = models.CharField(max_length=20, unique=True)
    description = models.TextField(max_length=200)
    created_date = models.DateTimeField(auto_now_add = True)
    created_user = models.OneToOneField(settings.AUTH_USER_MODEL)

    def __str__(self): 
        return self.title
    
class KeyWord(models.Model): 
    subject = models.OneToOneField(Subject, related_name='keywrods', on_delete=models.CASCADE)
    keyword = models.CharField(max_length=50)

    def __str__(self): 
        return self.keyword


class message(models.Model): 
    subject = models.OneToOneField(Subject, related_name='message', on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    file = models.FileField(blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add = True)

    def __str__(self): 
        return self.text
    
    class Meta:
        ordering = ['date']


class Favoris(models.Model): 
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, related_name='message', on_delete=models.CASCADE)

    def __str__(self):
        return self.subject + '/' + self.user
    
    class Meta:
        ordering = ['subject']






