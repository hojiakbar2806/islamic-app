from django.contrib import admin
from .models import TelegramUser, RamadanCalendar, BasicPrayer


admin.site.register(TelegramUser)
admin.site.register(RamadanCalendar)
admin.site.register(BasicPrayer)
