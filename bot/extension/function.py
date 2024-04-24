import requests
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import date, timedelta
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from bot.models import TelegramUser, RamadanCalendar
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


async def main_menu(context, chat_id):

    await context.bot.send_message(
        chat_id,
        'Asosiy oyna',
        reply_markup=ReplyKeyboardMarkup(
            [
                [
                    KeyboardButton('Namoz vaqti'),
                    KeyboardButton('Ramazon taqvimi')
                ],
                [
                    KeyboardButton('Duolar')
                ]
            ],

            resize_keyboard=True
        )
    )


async def send_location(context, chat_id):

    await context.bot.send_message(
        chat_id,
        'Joylashuvingizni ulashing',
        reply_markup=ReplyKeyboardMarkup(
            [
                [
                    KeyboardButton('Joylashuvni ulashish',
                                   request_location=True)
                ]
            ],
            resize_keyboard=True
        )
    )


async def save_user(update, context):
    from_user = update.message.from_user
    address_data = context.user_data.get('address', {})
    await sync_to_async(TelegramUser.objects.get_or_create)(chat_id=from_user.id, defaults={'first_name': from_user.first_name, 'tg_username': "@"+from_user.username})
    await context.bot.send_message(chat_id=from_user.id, text=f'Botimizga xush kelibsiz! {from_user.first_name}\nMalumotlaringiz saqlandi, endi davom ettirishingiz mumkin ')
    if address_data:
        await main_menu(context, chat_id=from_user.id)
    else:
        await send_location(context, chat_id=from_user.id)


async def save_location(update, context):
    chat_id = update.message.from_user.id
    user = await sync_to_async(TelegramUser.objects.get)(chat_id=chat_id)
    user.latitude = update.message.location.latitude
    user.longitude = update.message.location.longitude
    await sync_to_async(user.save)()
    await context.bot.send_message(chat_id=chat_id, text='Manzilingiz muvafaqiyatli saqlandi', reply_markup=ReplyKeyboardRemove())
    await main_menu(context, chat_id)


async def remove_message(context, chat_id, message_id):
    await context.bot.delete_message(
        chat_id, message_id=message_id)


async def request_namaz(context, chat_id, user, when='today'):
    latitude = user.latitude
    longitude = user.longitude

    today = date.today()+timedelta(hours=5)
    year = date.today().strftime("%Y")
    month = date.today().strftime("%m")

    if when == 'today':
        when = 'timings'
        target_date = today.strftime("%d-%m-%Y")
    if when == 'tomorrow':
        when = 'timings'
        target_date = (today + timedelta(days=1)).strftime("%d-%m-%Y")
    if when == 'month':
        when = 'calendar'
        target_date = f"{year}/{month}"

    response = requests.get(
        f'https://api.aladhan.com/v1/{when}/{target_date}?latitude={latitude}&longitude={longitude}&method=2')

    if response.status_code == 200:
        return response.json()
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=response.json()['data']
        )


async def send_namaz_time_for_day(context, chat_id, times, message_id=None):
    time = times['data']['timings']
    date = times['data']['date']
    caption = (
        f"<strong>🕌Namoz vaqtlari</strong>\n\n"
        f"Bomdod:\t\t{time['Fajr']}  (gacha saharlik)\n"
        f"Quyosh:\t\t{time['Sunrise']}\n"
        f"Peshin:\t\t{time['Dhuhr']}\n"
        f"Asr:\t\t{time['Asr']}\n"
        f"Shom:\t\t{time['Maghrib']}  (dan song iftor)\n"
        f"Xufton:\t\t{time['Isha']}\n\n"
        f"Hijriy \t{date['hijri']['date']}\n"
        f"Kalendar \t{date['gregorian']['date']}"
    )
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    'Bugungi',
                    callback_data="today"
                ),
                InlineKeyboardButton(
                    'Ertangi',
                    callback_data="tomorrow"
                ),
            ],
            [
                InlineKeyboardButton(
                    'Oylik',
                    callback_data="month"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Manzilni o'zgartirish",
                    callback_data="change_location"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Asosiy oyna",
                    callback_data="main_menu"
                ),
            ],
        ]
    )
    photo_url = 'https://www.muslimglobalrelief.org/wp-content/uploads/2023/03/mosque-building-fund.jpeg'

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=photo_url,
        caption=caption,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def send_namaz_time_for_month(context, chat_id, times):

    data = {'Sana': [], 'Bomdod': [], 'Quyosh': [],
            'Peshin': [], 'Asr': [], 'Shom': [], 'Xufton': []}

    for item in times['data']:
        date_readable = item['date']['readable']
        fajr = item['timings']['Fajr'].split(' ')[0]
        sunrise = item['timings']['Sunrise'].split(' ')[0]
        dhuhr = item['timings']['Dhuhr'].split(' ')[0]
        asr = item['timings']['Asr'].split(' ')[0]
        sunset = item['timings']['Sunset'].split(' ')[0]
        maghrib = item['timings']['Maghrib'].split(' ')[0]
        isha = item['timings']['Isha'].split(' ')[0]
        imsak = item['timings']['Imsak'].split(' ')[0]
        midnight = item['timings']['Midnight'].split(' ')[0]
        firstthird = item['timings']['Firstthird'].split(' ')[0]
        lastthird = item['timings']['Lastthird'].split(' ')[0]

        data['Sana'].append(date_readable)
        data['Bomdod'].append(fajr)
        data['Quyosh'].append(sunrise)
        data['Peshin'].append(dhuhr)
        data['Asr'].append(asr)
        data['Shom'].append(sunset)
        data['Xufton'].append(isha)

    df = pd.DataFrame(data)
    plt.figure(figsize=(10, 8), dpi=300)
    plt.axis('off')
    plt.table(cellText=df.values,
              colLabels=df.columns,
              cellLoc='center',
              loc='center',
              colColours=['#f5f5f5']*len(df.columns),
              colWidths=[0.16]*len(df.columns))
    bio = BytesIO()
    plt.savefig(bio, format='png', bbox_inches='tight')
    bio.seek(0)
    await context.bot.send_photo(chat_id=chat_id, photo=bio,
                                 caption='Shu oyning namoz vaqtlari',
                                 reply_markup=InlineKeyboardMarkup(
                                         [
                                             [
                                                 InlineKeyboardButton(
                                                     'Bugungi',
                                                     callback_data="today"
                                                 ),
                                                 InlineKeyboardButton(
                                                     'Ertangi',
                                                     callback_data="tomorrow"
                                                 ),
                                             ],
                                             [
                                                 InlineKeyboardButton(
                                                     'Oylik',
                                                     callback_data="month"
                                                 ),
                                             ],
                                             [
                                                 InlineKeyboardButton(
                                                     "Manzilni o'zgartirish",
                                                     callback_data="change_location"
                                                 ),
                                             ],
                                             [
                                                 InlineKeyboardButton(
                                                     "Asosiy oyna",
                                                     callback_data="main_menu"
                                                 ),
                                             ],
                                         ],

                                 ))
    plt.close()


async def send_regions_for_ramadan(context, chat_id):
    regions = await sync_to_async(lambda: list(RamadanCalendar.objects.all()))()

    buttons = [[InlineKeyboardButton(region.region_name, callback_data="region_"+str(region.id)) for region in regions][i:i+3]
               for i in range(0, len([InlineKeyboardButton(region.region_name, callback_data="region_"+str(region.id)) for region in regions]), 3)]
    buttons += [[InlineKeyboardButton('Asosiy oyna',
                                      callback_data="main_menu")]]

    await context.bot.send_message(
        text="Viloyatlardan birini tanlang",
        reply_markup=InlineKeyboardMarkup(buttons),
        chat_id=chat_id
    )


async def send_ramadan_calendar(context, chat_id, region_id):
    ramadan_calendar = await sync_to_async(get_object_or_404)(RamadanCalendar, id=region_id)
    await context.bot.send_photo(chat_id=chat_id, photo=ramadan_calendar.ramadan_image,
                                 caption=(
                                     f"{ramadan_calendar.region_name} ramazon vaqtlar"
                                 ),
                                 reply_markup=InlineKeyboardMarkup(
                                     [
                                         [
                                             InlineKeyboardButton(
                                                 'Oraga',
                                                 callback_data="region_back"
                                             ),
                                         ],
                                         [
                                             InlineKeyboardButton(
                                                 "Asosiy oyna",
                                                 callback_data="main_menu"
                                             ),
                                         ],

                                     ],

                                 ))
