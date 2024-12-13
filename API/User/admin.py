from django.contrib import admin

# Register your models here.
from API.User.models import User, Setting  # Importez votre modèle User ici

admin.site.register(User)
admin.site.register(Setting)