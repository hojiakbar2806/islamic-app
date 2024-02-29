from asgiref.sync import sync_to_async
from django.http import Http404
from django.shortcuts import get_object_or_404
from bot.extension.function import remove_message, main_menu, send_location, request_namaz, save_user, send_namaz_time_for_day, send_namaz_time_for_month, send_ramadan_calendar, send_regions_for_ramadan
from bot.models import TelegramUser


async def message_handler(update, context):
    message = update.message.text
    message_id = update.message.id
    chat_id = update.message.from_user.id

    try:
        user = await sync_to_async(get_object_or_404)(TelegramUser, chat_id=chat_id)
        if message in ['Namoz vaqti', 'Ramazon taqvimi']:
            if not user.longitude and not user.latitude:
                await send_location(context, chat_id)
            else:
                if message == 'Namoz vaqti':
                    times = await request_namaz(context, chat_id, user)
                    await remove_message(context, chat_id, message_id)
                    await send_namaz_time_for_day(context, chat_id, times)
                else:
                    await remove_message(context, chat_id, message_id)
                    await send_regions_for_ramadan(context, chat_id)

        if message == 'Duolar':
            print('duolar')
    except Http404:
        await save_user(update, context)


async def inline_message_handler(update, context):
    query = update.callback_query
    data = update.callback_query.data
    message_id = query.message.message_id
    chat_id = query.from_user.id
    user = await sync_to_async(TelegramUser.objects.get)(chat_id=chat_id)

    if data.split('_')[0] == 'region':
        if data == 'region_back':
            await remove_message(context, chat_id, message_id)
            await send_regions_for_ramadan(context, chat_id)
        else:
            await remove_message(context, chat_id, message_id)
            await send_ramadan_calendar(context, chat_id, region_id=data.split('_')[1])

    elif data in ["today", "tomorrow", "month"]:
        times = await request_namaz(context, chat_id, user, when=data)
        await remove_message(context, chat_id, message_id)
        if data in ["today", "tomorrow"]:
            await send_namaz_time_for_day(context, chat_id, times)
        else:
            await send_namaz_time_for_month(context, chat_id, times)
    elif data == "change_location":
        await remove_message(context, chat_id, message_id)
        await send_location(context, chat_id)
    elif data == "main_menu":
        await remove_message(context, chat_id, message_id)
        await main_menu(context, chat_id)
