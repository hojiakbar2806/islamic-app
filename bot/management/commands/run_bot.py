from django.core.management.base import BaseCommand
from bot.view import run_bot


class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **kwargs):
        run_bot()
