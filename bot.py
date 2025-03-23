import telebot
import cv2
import numpy as np
from rembg import remove
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7823908641:AAH-J7d1CZ3WOgMeolll8gavXsz6JqBk_A8"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "سلام! لطفاً یک عکس ارسال کنید و سپس یکی از گزینه‌های زیر را انتخاب کنید.")

# دریافت و ذخیره عکس
@bot.message_handler(content_types=['photo'])
def receive_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_path = f"input_{message.chat.id}.jpg"
    with open(file_path, "wb") as file:
        file.write(downloaded_file)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✨ حذف پس‌زمینه", callback_data="remove_bg"))
    markup.add(InlineKeyboardButton("🔍 افزایش وضوح", callback_data="sharpen"))

    bot.send_message(message.chat.id, "عکس دریافت شد. یکی از گزینه‌ها را انتخاب کنید:", reply_markup=markup)

# پردازش دکمه‌های شیشه‌ای
@bot.callback_query_handler(func=lambda call: call.data in ["remove_bg", "sharpen"])
def handle_buttons(call):
    if not call.message.reply_to_message or not call.message.reply_to_message.photo:
        bot.send_message(call.message.chat.id, "❌ لطفاً ابتدا یک عکس ارسال کنید و سپس دکمه را بزنید!")
        return

    file_path = f"input_{call.message.chat.id}.jpg"

    if call.data == "remove_bg":
        remove_background(call.message, file_path)
    elif call.data == "sharpen":
        sharpen_image(call.message, file_path)

# حذف پس‌زمینه عکس
def remove_background(message, file_path):
    img = cv2.imread(file_path)
    output = remove(img)
    output_path = f"no_bg_{message.chat.id}.png"
    cv2.imwrite(output_path, output)

    with open(output_path, "rb") as final_file:
        bot.send_photo(message.chat.id, final_file)

# افزایش وضوح عکس
def sharpen_image(message, file_path):
    img = cv2.imread(file_path)

    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])

    sharpened = cv2.filter2D(img, -1, kernel)
    output_path = f"sharpened_{message.chat.id}.jpg"
    cv2.imwrite(output_path, sharpened)

    with open(output_path, "rb") as sharp_file:
        bot.send_photo(message.chat.id, sharp_file)

bot.polling()
