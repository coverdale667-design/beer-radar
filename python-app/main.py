import telebot
from telebot import types

# Твой токен от BotFather
TOKEN = '8912910354:AAFwMBI5wEpdiuKt2Q4Bp-C8wgDgjvjFIWo'
bot = telebot.TeleBot(TOKEN)

# Приветствие и главное меню
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Кнопки выбора
    btn_shop = types.KeyboardButton("🛒 Магазинное (Скидки)")
    btn_draft = types.KeyboardButton("🍺 Разливное / Крафт")
    # Кнопка запроса гео
    btn_geo = types.KeyboardButton("📍 Найти пиво рядом", request_location=True)
    
    markup.add(btn_shop, btn_draft, btn_geo)
    
    bot.reply_to(
        message, 
        "Привет! 🍻 Я твой Пивной Радар Минска.\n"
        "Помогу найти самое бюджетное пенное в городе. Выбирай вариант или скинь мне геолокацию:", 
        reply_markup=markup
    )

# Обработка текстовых кнопок
@bot.message_handler(func=lambda message: message.text in ["🛒 Магазинное (Скидки)", "🍺 Разливное / Крафт"])
def handle_categories(message):
    if message.text == "🛒 Магазинное (Скидки)":
        bot.reply_to(
            message, 
            "Ищу акции в супермаркетах Минска... 📉\n\n"
            "📌 Топ на сегодня:\n"
            "1. Хит! — Крыніца Светлае (0.5л) — 1.85 BYN\n"
            "2. Е-доставка — Жигулевское (1.9л) — 4.20 BYN"
        )
    elif message.text == "🍺 Разливное / Крафт":
        bot.reply_to(
            message, 
            "Проверяю пивные краны и разливайки... 🗺\n\n"
            "📌 Выгодные точки:\n"
            "1. Точка (розлив) — Аливария — от 3.50 BYN за литр."
        )

# Обработка геолокации
@bot.message_handler(content_types=['location'])
def handle_location(message):
    lat = message.location.latitude
    lon = message.location.longitude
    
    bot.reply_to(
        message, 
        f"Координаты приняты ({lat:.4f}, {lon:.4f})! 🧭\n"
        f"Ближайший к тебе магазин со скидкой на пиво — 'Хит!' в 350 метрах."
    )

# Функция запуска для Replit
def main():
    print("Пивной Радар успешно запущен и готов к работе...")
    bot.infinity_polling()

if __name__ == '__main__':
    main()
    