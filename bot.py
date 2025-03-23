import telebot
import cv2
import numpy as np
from rembg import remove
from flask import Flask
import threading

# توکن ربات تلگرام
TOKEN = "ت7528697005:AAE_Cs0dWfmQbCXHpQEzYFDPK2TDrf4CUww"
bot = telebot.TeleBot(TOKEN)

# سرور Flask برای آنلاین ماندن در Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# اجرای Flask در یک ترد جداگانه
threading.Thread(target=run_flask, daemon=True).start()

# پیام خوش‌آمدگویی
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! یک عکس بفرست تا پردازشش کنم.\n\n"
                          "دستورات:\n"
                          "/cartoon - کارتونی کردن عکس 🎨\n"
                          "/remove_bg - حذف پس‌زمینه 🔄\n"
                          "/sharpen - افزایش وضوح 🔍")

# ذخیره عکس دریافتی
def save_photo(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("input.jpg", "wb") as file:
            file.write(downloaded_file)
        return True
    except Exception as e:
        bot.reply_to(message, "❌ خطایی رخ داد! دوباره امتحان کن.")
        print(f"Error in save_photo: {e}")
        return False

# کارتونی کردن عکس
@bot.message_handler(commands=['cartoon'])
def cartoonize_image(message):
    if not save_photo(message):
        return

    img = cv2.imread("input.jpg")
    if img is None:
        bot.reply_to(message, "❌ عکس نامعتبر است!")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    cv2.imwrite("cartoon.jpg", cartoon)
    with open("cartoon.jpg", "rb") as cartoon_file:
        bot.send_photo(message.chat.id, cartoon_file)

# حذف پس‌زمینه عکس
@bot.message_handler(commands=['remove_bg'])
def remove_background(message):
    if not save_photo(message):
        return

    try:
        with open("input.jpg", "rb") as inp_file:
            img = inp_file.read()

        output = remove(img)

        with open("no_bg.png", "wb") as out_file:
            out_file.write(output)

        with open("no_bg.png", "rb") as final_file:
            bot.send_photo(message.chat.id, final_file)
    except Exception as e:
        bot.reply_to(message, "❌ خطایی در پردازش حذف پس‌زمینه رخ داد!")
        print(f"Error in remove_background: {e}")

# افزایش وضوح (Sharpening)
@bot.message_handler(commands=['sharpen'])
def sharpen_image(message):
    if not save_photo(message):
        return

    img = cv2.imread("input.jpg")
    if img is None:
        bot.reply_to(message, "❌ عکس نامعتبر است!")
        return

    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])  # ماتریس شارپنینگ

    sharpened = cv2.filter2D(img, -1, kernel)
    cv2.imwrite("sharpened.jpg", sharpened)

    with open("sharpened.jpg", "rb") as sharp_file:
        bot.send_photo(message.chat.id, sharp_file)

# اجرای ربات
bot.polling()
