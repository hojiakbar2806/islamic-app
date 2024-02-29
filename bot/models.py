from django.db import models


class TelegramUser(models.Model):
    chat_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    tg_username = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tg_username} - {self.chat_id}'


class RamadanCalendar(models.Model):
    region_name = models.CharField(max_length=100)
    ramadan_image = models.ImageField(upload_to='media/ramadan_calendar')

    def __str__(self):
        return f"{self.id} {self.region_name}"

    class Meta:
        ordering = ['id']


class BasicPrayer(models.Model):
    prayer_name = models.CharField(max_length=100)
    prayer_text = models.TextField(max_length=500)

    def __str__(self):
        return f'{self.prayer_name}'
