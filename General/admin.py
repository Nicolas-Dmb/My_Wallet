from django.contrib import admin
from General.models import Asset,OneYearValue, OldValue, Currency

# Register your models here.
admin.site.register(Asset)
admin.site.register(OneYearValue)
admin.site.register(OldValue)
admin.site.register(Currency)
