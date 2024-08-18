from django.db import models
from User.models import User
from django.conf import settings
from django.db import transaction
import datetime

'''
- Un user créer plus sujets.
- Deux user ont des Keywords similaires.
- deux user parlent dans un sujets similaires l'un envoie une photo et par l'autre.
- un User met un ou des sujets favoris. 
- un user recherche par keywords des sujets
'''


class Subject(models.Model):
    title = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add = True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    #subject activity
    weekly_messages = models.IntegerField(default=0)
    week = models.IntegerField(default=0)

    @transaction.atomic
    def count_message(self):
        today = datetime.datetime.today()
        week_num = today.isocalendar()[1]
        if self.week == week_num : 
            self.weekly_messages += 1
        else : 
            self.week = week_num
            self.weekly_messages = 1
        self.save()
    
    @transaction.atomic
    def know_subject_activity(self):
        today = datetime.datetime.today()
        week_num = today.isocalendar()[1]
        if self.week == week_num : 
            return self.weekly_messages
        else : 
            self.week = week_num
            self.weekly_messages = 0
            self.save()
            return self.weekly_messages

    def __str__(self): 
        return self.title
    
class KeyWord(models.Model): 
    subject = models.ForeignKey(Subject,related_name='keyword', on_delete=models.CASCADE)
    keyword = models.CharField(max_length=50)

    def __str__(self): 
        return self.keyword

class Message(models.Model): 
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    file = models.FileField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add = True)

    def __str__(self): 
        return self.text
    
    class Meta:
        ordering = ['-date']


class Favori(models.Model): 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.subject.title}"
    
    class Meta:
        ordering = ['subject']






