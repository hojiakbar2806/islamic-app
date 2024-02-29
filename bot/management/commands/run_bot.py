from django.core.management.base import BaseCommand
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from bot.extension import TOKEN, message_handler, inline_message_handler
from bot.extension.function import save_location, save_user


async def start_async(update, context):
    await save_user(update, context)


class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        app = ApplicationBuilder().token(TOKEN).build()

        app.add_handler(CommandHandler('start', start_async))
        app.add_handler(MessageHandler(filters.TEXT, message_handler))
        app.add_handler(CallbackQueryHandler(inline_message_handler))
        app.add_handler(MessageHandler(filters.LOCATION, save_location))

        app.run_polling()
