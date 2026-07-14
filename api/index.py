import os
import telebot
from telebot import types
import requests
import math
from flask import Flask, request

TOKEN = '8912910354:AAFwMBI5wEpdiuKt2Q4Bp-C8wgDgjvjFIWo'
bot = telebot.TeleBot(TOKEN, threaded=False)

app = Flask(__name__)

# Реальные пивные точки в Минске для теста поиска рядом
BEER_PLACES = [
    {
        "name": "Дискаунтер 'Грошык' (дешевое баночное)",
        "address": "ул. Козлова, 30",
        "lat": 53.9068,
        "lon": 27.5925,
        "info": "Крыніца Светлае — 1.79 BYN"
    },
    {
        "name": "Магазин 'Хит! Экспресс' (акции)",
        "address": "ул. Ленина, 5",
        "lat": 53.9009,
        "lon": 27.5587,
        "info": "Аливария 10-ка (0.9л) — 2.49 BYN"
    },
    {
        "name": "Магазин разливного пива 'Точка'",
        "address": "ул. Бельского, 10",
        "lat": 53.9015,
        "lon": 27.4811,
        "info": "Аливария на розлив от 3.50 BYN/л"
    },
    {
        "name": "Пивной магазин 'Бавария'",
        "address": "пр. Дзержинского, 119",
        "lat": 53.8492,
        "lon": 27.4743,
        "info": "Лидское от 3.80 BYN/л"
    },
    {
        "name": "Бар-магазин крафта 'Spin Bar'",
        "address": "ул. Кальварийская, 21",
        "lat": 53.9056,
        "lon": 27.5276,
        "info": "Локальный крафт от 6.50 BYN"
    }
]

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Радиус Земли в метрах
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# Запасной список скидок
def get_fallback_discounts():
    return (
        "🛒 *Актуальные скидки в сетях Минска:*\n\n"
        "1. *Хит!* — Аливария 10-ка (0.9л) — *2.49 BYN*\n"
        "2. *Грошык* — Крыніца Светлае (0.5л) — *1.79 BYN*\n"
        "3. *Е-доставка* — Жигулевское Специальное (1.9л) — *4.15 BYN*\n"
        "4. *Санта* — Бобров Светлое (0.45л) — *1.69 BYN*"
    )

# Приветствие
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_shop = types.KeyboardButton("🛒 Магазинное (Скидки)")
    btn_draft = types.KeyboardButton("🍺 Разливное / Крафт")
    btn_geo = types.KeyboardButton("📍 Найти пиво рядом", request_location=True)
    markup.add(btn_shop, btn_draft, btn_geo)
    
    bot.reply_to(
        message, 
        "Привет! 🍻 Я твой Пивной Радар Минска.\n"
        "Выбирай категорию, и я найду лучшие цены:", 
        reply_markup=markup
    )

# Обработка нажатий
@bot.message_handler(func=lambda message: message.text in ["🛒 Магазинное (Скидки)", "🍺 Разливное / Крафт"])
def handle_categories(message):
    if message.text == "🛒 Магазинное (Скидки)":
        beer_list = get_fallback_discounts()
        bot.send_message(message.chat.id, beer_list, parse_mode="Markdown")
        
    elif message.text == "🍺 Разливное / Крафт":
        bot.reply_to(
            message, 
            "🍺 *Разливное пиво в Минске:*\n\n"
            "• *Точка* (ул. Бельского, 10) — Аливария на розлив от *3.50 BYN/л*\n"
            "• *Бавария* (пр. Дзержинского, 119) — Лидское от *3.80 BYN/л*\n"
            "• *Крафтмэн* (ул. Гикало, 5) — крафтовый локальный стаут от *7.50 BYN/бокал*",
            parse_mode="Markdown"
        )

# Геологическая координация
@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_lat = message.location.latitude
    user_lon = message.location.longitude
    minsk_center_lat = 53.9025
    minsk_center_lon = 27.5614
    
    distance_to_minsk = calculate_distance(user_lat, user_lon, minsk_center_lat, minsk_center_lon)
    is_teleport = False
    if distance_to_minsk > 50000:
        user_lat = minsk_center_lat
        user_lon = minsk_center_lon
        is_teleport = True
    
    nearest_place = None
    min_dist = float('inf')
    for place in BEER_PLACES:
        dist = calculate_distance(user_lat, user_lon, place["lat"], place["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest_place = place
            
    response = ""
    if is_teleport:
        response += "📍 *Режим тестирования:* Вижу, что ты не в Минске. Виртуально переношу тебя на ст.м. Октябрьская! 🚇\n\n"
        
    response += f"🎯 *Ближайшая пивная точка найдена!*\n\n"
    response += f"🏪 *{nearest_place['name']}*\n"
    response += f"📍 Адрес: {nearest_place['address']}\n"
    response += f"🍻 Что почем: {nearest_place['info']}\n"
    
    if min_dist < 1000:
        response += f"🚶‍♂️ Расстояние: всего *{int(min_dist)} метров* от тебя!"
    else:
        response += f"🚗 Расстояние: *{min_dist/1000:.1f} км* от тебя."
        
    bot.reply_to(message, response, parse_mode="Markdown")

# Настройки роутинга для Vercel (вебхук принимает POST-запросы от Telegram)
@app.route('/', methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/', methods=['GET'])
def index():
    return "Бот работает на Vercel!", 200
    