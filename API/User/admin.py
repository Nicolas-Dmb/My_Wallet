from django.contrib import admin

# Register your models here.
from .models import User  # Importez votre modèle User ici

admin.site.register(User)