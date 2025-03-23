import telebot
import cv2
import numpy as np
from rembg import remove
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

TOKEN = "7823908641:AAH-J7d1CZ3WOgMeolll8gavXsz6JqBk_A8"  # توکن ربات شما
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✨ حذف پس‌زمینه", callback_data="remove_bg"))
    markup.add(InlineKeyboardButton("🔍 افزایش وضوح", callback_data="sharpen"))
    
    bot.send_message(message.chat.id, "سلام! یک عکس بفرست و سپس یکی از گزینه‌ها را انتخاب کن:", reply_markup=markup)

# ذخیره عکس دریافتی
def save_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("input.jpg", "wb") as file:
        file.write(downloaded_file)

    return "input.jpg"

# هندل کردن دکمه‌های شیشه‌ای
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.message.photo:
        file_path = save_photo(call.message)
        
        if call.data == "remove_bg":
            remove_background(call.message, file_path)
        elif call.data == "sharpen":
            sharpen_image(call.message, file_path)
    else:
        bot.send_message(call.message.chat.id, "لطفاً اول یک عکس بفرستید!")

# حذف پس‌زمینه عکس
def remove_background(message, file_path):
    with open(file_path, "rb") as inp_file:
        img = inp_file.read()

    output = remove(img)

    with open("no_bg.png", "wb") as out_file:
        out_file.write(output)

    with open("no_bg.png", "rb") as final_file:
        bot.send_photo(message.chat.id, final_file)

# افزایش وضوح عکس
def sharpen_image(message, file_path):
    img = cv2.imread(file_path)

    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])

    sharpened = cv2.filter2D(img, -1, kernel)
    cv2.imwrite("sharpened.jpg", sharpened)

    with open("sharpened.jpg", "rb") as sharp_file:
        bot.send_photo(message.chat.id, sharp_file)

# اجرای Flask در یک ترد جداگانه
threading.Thread(target=run_flask).start()

# اجرای ربات تلگرام
bot.polling()
