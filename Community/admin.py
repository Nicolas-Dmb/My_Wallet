from django.contrib import admin
from Community.models import Subject, KeyWord, Message, Favori

# Register your models here.
admin.site.register(Subject)
admin.site.register(KeyWord)
admin.site.register(Message)
admin.site.register(Favori)