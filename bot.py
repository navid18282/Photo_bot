import telebot
import cv2
import numpy as np
import os
from rembg import remove
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# توکن واقعی ربات تلگرام
TOKEN = "7823908641:AAH-J7d1CZ3WOgMeolll8gavXsz6JqBk_A8"

# آدرس نهایی سرویس در Render (در پایان دیپلوی بهت می‌دهد)
# مثلاً: "https://photo-bot-xxxxx.onrender.com/"
WEBHOOK_URL = "https://نام-سایت-شما.onrender.com/"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ساخت پوشه برای ذخیره تصاویر (در صورت وجود نداشتن)
if not os.path.exists("images"):
    os.makedirs("images")

# دیکشنری برای نگه‌داری مسیر عکس‌های آخر هر کاربر
user_images = {}

@app.route("/", methods=["GET"])
def home():
    return "ربات در حال اجرا است!"

@app.route("/", methods=["POST"])
def receive_update():
    # دریافت آپدیت تلگرام از طریق وبهوک
    update = request.get_data().decode("utf-8")
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "!", 200

# حذف وبهوک قبلی و تنظیم وبهوک جدید
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✨ حذف پس‌زمینه", callback_data="remove_bg"))
    markup.add(InlineKeyboardButton("🔍 افزایش وضوح", callback_data="sharpen"))
    
    bot.send_message(
        message.chat.id,
        "سلام! لطفاً یک عکس ارسال کنید، سپس یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=markup
    )

@bot.message_handler(content_types=['photo'])
def save_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_path = f"images/{message.chat.id}.jpg"
    with open(file_path, "wb") as file:
        file.write(downloaded_file)

    user_images[message.chat.id] = file_path

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✨ حذف پس‌زمینه", callback_data="remove_bg"))
    markup.add(InlineKeyboardButton("🔍 افزایش وضوح", callback_data="sharpen"))
    
    bot.send_message(
        message.chat.id,
        "✅ عکس دریافت شد. حالا یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    user_id = call.message.chat.id

    if user_id not in user_images:
        bot.send_message(user_id, "❌ لطفاً ابتدا یک عکس ارسال کنید و سپس دکمه را بزنید!")
        return

    file_path = user_images[user_id]

    if call.data == "remove_bg":
        remove_background(user_id, file_path)
    elif call.data == "sharpen":
        sharpen_image(user_id, file_path)

def remove_background(user_id, file_path):
    with open(file_path, "rb") as inp_file:
        img = inp_file.read()

    output = remove(img)

    output_path = f"images/{user_id}_no_bg.png"
    with open(output_path, "wb") as out_file:
        out_file.write(output)

    with open(output_path, "rb") as final_file:
        bot.send_photo(user_id, final_file)

def sharpen_image(user_id, file_path):
    img = cv2.imread(file_path)

    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    sharpened = cv2.filter2D(img, -1, kernel)
    output_path = f"images/{user_id}_sharpened.jpg"
    cv2.imwrite(output_path, sharpened)

    with open(output_path, "rb") as sharp_file:
        bot.send_photo(user_id, sharp_file)

if __name__ == "__main__":
    # اجرا روی پورت تعیین‌شده توسط Render یا پورت 5000 به‌صورت پیش‌فرض
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
