from flask import Flask, request
import telebot

TOKEN = "8912910354:AAFwMBI5wEpdiuKt2Q4Bp-C8wgDgjvjFIWo"
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Главная страница для проверки в браузере
@app.route('/', methods=['GET'])
def index():
    return "Бот пиво-радар работает на Vercel!"

# Точка, куда Telegram присылает сообщения (вебхук)
@app.route('/api/index', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Invalid content type', 400

# Пример обработки команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Пиво-радар в Минске запущен. Чем могу помочь?")

# Пример обработки любого текстового сообщения
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Вы написали: {message.text}")
    