from flask import Flask, request
import telebot
from telebot import types
import requests
import math

TOKEN = "8912910354:AAFwMBI5wEpdiuKt2Q4Bp-C8wgDgjvjFIWo"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# ──────────────────────────────────────────
# База пивных точек Минска
# ──────────────────────────────────────────
BEER_PLACES = [
    {
        "name": "Дискаунтер 'Грошык' (дешевое баночное)",
        "address": "ул. Козлова, 30",
        "lat": 53.9068,
        "lon": 27.5925,
        "info": "Крыніца Светлае — 1.79 BYN",
        "type": "shop"
    },
    {
        "name": "Магазин 'Хит! Экспресс' (акции)",
        "address": "ул. Ленина, 5",
        "lat": 53.9009,
        "lon": 27.5587,
        "info": "Аливария 10-ка (0.9л) — 2.49 BYN",
        "type": "shop"
    },
    {
        "name": "Магазин разливного пива 'Точка'",
        "address": "ул. Бельского, 10",
        "lat": 53.9015,
        "lon": 27.4811,
        "info": "Аливария на розлив от 3.50 BYN/л",
        "type": "draft"
    },
    {
        "name": "Пивной магазин 'Бавария'",
        "address": "пр. Дзержинского, 119",
        "lat": 53.8492,
        "lon": 27.4743,
        "info": "Лидское от 3.80 BYN/л",
        "type": "draft"
    },
    {
        "name": "Бар-магазин крафта 'Spin Bar'",
        "address": "ул. Кальварийская, 21",
        "lat": 53.9056,
        "lon": 27.5276,
        "info": "Локальный крафт от 6.50 BYN",
        "type": "craft"
    }
]

# ──────────────────────────────────────────
# Утилиты
# ──────────────────────────────────────────
def calculate_distance(lat1, lon1, lat2, lon2):
    """Формула Гаверсинуса — расстояние в метрах."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_edostavka_beer():
    """Пробуем получить данные с Е-доставки, иначе — запасной список."""
    try:
        url = "https://e-dostavka.by/api/v1/search"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        params = {"query": "пиво", "sort": "price_asc", "limit": 5}
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        if resp.status_code == 200:
            products = resp.json().get("products", [])
            if products:
                text = "🛒 *Топ дешевого пива из Е-доставки:*\n\n"
                for i, p in enumerate(products, 1):
                    text += f"{i}. {p.get('name','?')} — *{p.get('price',0)/100:.2f} BYN*\n"
                return text
    except Exception:
        pass
    return get_fallback_discounts()

def get_fallback_discounts():
    return (
        "🛒 *Актуальные скидки в сетях Минска:*\n\n"
        "1. *Хит!* — Аливария 10-ка (0.9л) — *2.49 BYN*\n"
        "2. *Грошык* — Крыніца Светлае (0.5л) — *1.79 BYN*\n"
        "3. *Е-доставка* — Жигулевское Специальное (1.9л) — *4.15 BYN*\n"
        "4. *Санта* — Бобров Светлое (0.45л) — *1.69 BYN*"
    )

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Выбрать магазин"),
        types.KeyboardButton("Отправить GPS", request_location=True)
    )
    return markup

def shop_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🛒 Магазины (акции)"),
        types.KeyboardButton("🍺 Разливное / Крафт"),
        types.KeyboardButton("📋 Все адреса"),
        types.KeyboardButton("🔙 Назад")
    )
    return markup

# ──────────────────────────────────────────
# Обработчики
# ──────────────────────────────────────────
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Привет! 🍻 Я твой *Пивной Радар Минска*.\nВыбирай категорию или пришли геолокацию:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "Выбрать магазин")
def handle_choose_shop(message):
    bot.send_message(
        message.chat.id,
        "Выбери раздел 👇",
        reply_markup=shop_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🛒 Магазины (акции)")
def handle_shops(message):
    bot.send_message(message.chat.id, "🔌 Подключаюсь к базам магазинов, секунду...")
    bot.send_message(message.chat.id, get_edostavka_beer(), parse_mode="Markdown", reply_markup=shop_menu())

@bot.message_handler(func=lambda m: m.text == "🍺 Разливное / Крафт")
def handle_draft(message):
    bot.send_message(
        message.chat.id,
        "🍺 *Разливное пиво в Минске:*\n\n"
        "• *Точка* (ул. Бельского, 10) — Аливария от *3.50 BYN/л*\n"
        "• *Бавария* (пр. Дзержинского, 119) — Лидское от *3.80 BYN/л*\n"
        "• *Spin Bar* (ул. Кальварийская, 21) — крафт от *6.50 BYN*",
        parse_mode="Markdown",
        reply_markup=shop_menu()
    )

@bot.message_handler(func=lambda m: m.text == "📋 Все адреса")
def handle_all_addresses(message):
    text = "📋 *Все пивные точки в базе:*\n\n"
    for p in BEER_PLACES:
        text += f"🏪 *{p['name']}*\n📍 {p['address']}\n🍻 {p['info']}\n\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=shop_menu())

@bot.message_handler(func=lambda m: m.text == "🔙 Назад")
def handle_back(message):
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu())

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_lat = message.location.latitude
    user_lon = message.location.longitude

    minsk_lat, minsk_lon = 53.9025, 27.5614
    dist_to_minsk = calculate_distance(user_lat, user_lon, minsk_lat, minsk_lon)

    is_teleport = dist_to_minsk > 50000
    if is_teleport:
        user_lat, user_lon = minsk_lat, minsk_lon

    nearest = min(BEER_PLACES, key=lambda p: calculate_distance(user_lat, user_lon, p["lat"], p["lon"]))
    min_dist = calculate_distance(user_lat, user_lon, nearest["lat"], nearest["lon"])

    response = ""
    if is_teleport:
        response += "📍 *Режим тестирования:* Вижу, что ты не в Минске. Виртуально переношу тебя на ст.м. Октябрьская! 🚇\n\n"

    response += (
        f"🎯 *Ближайшая пивная точка:*\n\n"
        f"🏪 *{nearest['name']}*\n"
        f"📍 Адрес: {nearest['address']}\n"
        f"🍻 {nearest['info']}\n"
    )
    if min_dist < 1000:
        response += f"🚶‍♂️ Расстояние: *{int(min_dist)} метров* от тебя!"
    else:
        response += f"🚗 Расстояние: *{min_dist/1000:.1f} км* от тебя."

    bot.send_message(message.chat.id, response, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(
        message.chat.id,
        "Используй кнопки ниже или пришли геолокацию 📍",
        reply_markup=main_menu()
    )

# ──────────────────────────────────────────
# Flask routes
# ──────────────────────────────────────────
@app.route('/', methods=['GET'])
def index():
    return "Бот пиво-радар работает на Vercel!"

@app.route('/api/index', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Invalid content type', 400
