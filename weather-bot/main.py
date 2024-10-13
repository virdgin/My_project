"""Телеграм-бот для получения информации о погоде."""

import math
import requests
import telebot


BOT_API_TOKEN = "7570063289:AAFl5bXstwxvUAfnOXqJmomHZJmlerurshk"
bot = telebot.TeleBot(BOT_API_TOKEN)
WEATHER_API_TOKEN = '896cbce77135f7cbd823c27bdf6d8b6a'


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 'Привет. Этот бот показывает погоду в вашем городе. Введите город')
    bot.register_next_step_handler_by_chat_id(message.chat.id, weather)


def weather(message):
    city = message.text.title()
    try:
        response = requests.get(f'http://api.weatherstack.com/current?access_key={WEATHER_API_TOKEN}&query={city}&units=m')
        data = response.json()
        city = data['location']["name"]
        cur_temp = data["current"]["temperature"]
        humidity = data["current"]["humidity"]
        pressure = data["current"]["pressure"]
        wind = round(data["current"]["wind_speed"] * 1000 / 3600, 1)
        text = f"На {data['location']['localtime']} в {city}:\nТемпература воздуха {cur_temp} C, Скороcть ветра {wind} м/с,\nОтносительная влажность {humidity}%, Давление {math.ceil(pressure/1.333)} мм.рт.ст"
        bot.send_message(message.chat.id, text)
    except:
        bot.send_message(message.chat.id, 'Попробуйте другой город')
        bot.register_next_step_handler_by_chat_id(message.chat.id, weather)


bot.infinity_polling()
