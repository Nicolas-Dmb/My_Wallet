from django.contrib import admin
from .models import Asset,OneYearValue, OldValue

# Register your models here.
admin.site.register(Asset)
admin.site.register(OneYearValue)
admin.site.register(OldValue)
