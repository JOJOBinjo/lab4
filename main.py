import telebot
import requests
import json
from telebot import types

bot = telebot.TeleBot("в отчете")
API = "в отчете"

user_city = {}
main_city = {}
waiting_new_main_city = set()


def get_keyboard(chat_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if chat_id in main_city:
        keyboard.add(
            f"Показать температуру ({main_city[chat_id]})",
            "Сменить основной город"
        )
    else:
        keyboard.add("Сделать основным городом")

    return keyboard


def send_weather_by_city(chat_id, city):
    res = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": city,
            "appid": API,
            "units": "metric",
            "lang": "ru"
        }
    )

    if res.status_code != 200:
        bot.send_message(chat_id, "Город не найден")
        return False

    data = json.loads(res.text)
    temp = data["main"]["temp"]

    bot.send_message(
        chat_id,
        f"🌤 Сейчас погода в {city}: {temp}°C\n\n Можете ввести другой город, сделать его основным для быстрого показа погоды, или заменить его на другой",
        reply_markup=get_keyboard(chat_id)
    )
    return True


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Введите название города"
    )


@bot.message_handler(func=lambda m: m.text.startswith("Показать температуру"))
def show_main_city_weather(message):
    chat_id = message.chat.id
    city = main_city.get(chat_id)

    if not city:
        bot.send_message(chat_id, "Основной город не выбран")
        return

    send_weather_by_city(chat_id, city)


@bot.message_handler(func=lambda m: m.text == "Сделать основным городом")
def set_main_city(message):
    chat_id = message.chat.id

    if chat_id not in user_city:
        bot.send_message(chat_id, "Сначала введите город")
        return

    main_city[chat_id] = user_city[chat_id]

    bot.send_message(
        chat_id,
        f"Город «{main_city[chat_id]}» выбран как основной",
        reply_markup=get_keyboard(chat_id)
    )


@bot.message_handler(func=lambda m: m.text == "Сменить основной город")
def change_main_city(message):
    chat_id = message.chat.id
    waiting_new_main_city.add(chat_id)

    bot.send_message(
        chat_id,
        "✏️ Введите новый основной город"
    )


@bot.message_handler(content_types=["text"])
def handle_city_input(message):
    chat_id = message.chat.id
    city = message.text.strip()

    user_city[chat_id] = city


    if chat_id in waiting_new_main_city:
        waiting_new_main_city.remove(chat_id)
        main_city[chat_id] = city

    success = send_weather_by_city(chat_id, city)

    if not success:
        return




bot.polling(none_stop=True)