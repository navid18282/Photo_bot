import telebot
import cv2
import numpy as np
from rembg import remove
from flask import Flask
from PIL import Image
import io
import os

TOKEN = "7823991986:AAEZ4VRH9D6f-XBPEJC2XZPpaoy31Zzc1ek"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! یک عکس بفرست تا پردازشش کنم.\n\n"
                          "دستورات موجود:\n"
                          "/cartoon - کارتونی کردن عکس 🎨\n"
                          "/remove_bg - حذف پس‌زمینه 🔄\n"
                          "/sharpen - افزایش وضوح 🔍")

def save_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("input.jpg", "wb") as file:
        file.write(downloaded_file)

@bot.message_handler(commands=['cartoon'])
def cartoonize_image(message):
    save_photo(message)
    img = cv2.imread("input.jpg")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

    color = cv2.bilateralFilter(img, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    cv2.imwrite("cartoon.jpg", cartoon)

    with open("cartoon.jpg", "rb") as cartoon_file:
        bot.send_photo(message.chat.id, cartoon_file)

@bot.message_handler(commands=['remove_bg'])
def remove_background(message):
    save_photo(message)

    with open("input.jpg", "rb") as inp_file:
        img = Image.open(io.BytesIO(inp_file.read()))
    
    output = remove(img)  # حذف پس‌زمینه

    output.save("no_bg.png")  # ذخیره عکس جدید

    with open("no_bg.png", "rb") as final_file:
        bot.send_photo(message.chat.id, final_file)

@bot.message_handler(commands=['sharpen'])
def sharpen_image(message):
    save_photo(message)
    img = cv2.imread("input.jpg")

    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])  # ماتریس شارپنینگ

    sharpened = cv2.filter2D(img, -1, kernel)
    cv2.imwrite("sharpened.jpg", sharpened)

    with open("sharpened.jpg", "rb") as sharp_file:
        bot.send_photo(message.chat.id, sharp_file)

import threading
def run_bot():
    bot.polling()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
