#=========================
# Made by matin357 in 2025
#=========================
import json, sqlite3, telebot, os, sys, hashlib
from telebot import types


# ==========================
# Інніціалізація бази данних
# ==========================

con = sqlite3.connect("information/verification.db", check_same_thread=False)
cur = con.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS ver (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tg_id INTEGER NOT NULL
)''')
con.commit()


# ================
# Отримання токена
# ================

with open("tocken.txt", "r") as file_with_token:
    token = file_with_token.readline().strip()
bot = telebot.TeleBot(token)


# =================
# Допоміжні функції
# =================

def is_command(text):
    return text.startswith('/')

def open_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
def save_json(path,data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    

# ===============
# Основні функції
# ===============

def new_directory(message):
    if is_command(message.text):
        bot.send_message(message.chat.id, "❌ Ви вийшли зы створення новоъ папки.")
        return

    folder_name = message.text.strip()
    SAVE_DIR = os.path.join("files", folder_name)
    os.makedirs(SAVE_DIR, exist_ok=True)
    bot.send_message(message.chat.id, f"✅ Папка '{folder_name}' створена!")

def new_teacher(message):
    if is_command(message.text):
        bot.send_message(message.chat.id, "❌ Ви вийшли з додавання вчителя.")
        return
    try:
        teacher = str(message.text.strip())
        teacher_id = hashlib.md5(teacher.encode()).hexdigest()
        data = open_json('information/admins.json')
        data["teachers_id"].append(teacher_id)
        save_json("information/admins.json", data)
        bot.send_message(message.chat.id, '✅ Нового вчитєля додано')
    except ValueError:
        bot.send_message(message.chat.id, "❌Невірний запис id")

def new_admin(message):
    if is_command(message.text):
        bot.send_message(message.chat.id, "❌ Ви вийшли з додавання адміна.")
        return
    try:
        admin =str(message.text.strip())
        admin_id = hashlib.md5(admin.encode()).hexdigest()
        data = open_json('information/admins.json')
        data["admins_id"].append(admin_id)
        save_json('information/admins.json', data)
        bot.send_message(message.chat.id, '✅ Нового адміна додано')
    except ValueError:
        bot.send_message(message.chat.id, "❌Невірний запис id")

def show_verification(message):
    cur.execute("SELECT * FROM ver")
    result = cur.fetchall()
    if not result:
        bot.send_message(message.chat.id, "📭 Заявок поки що немає.")
        return
    text = "📋 Список усіх заявок:\n\n"
    for row in result:
        text += f"🆔 {row[0]} | 👤 {row[1]} | 💬 {row[2]}\n"
        bot.send_message(message.chat.id, text)

def save_file_to_folder(message, folder_name):
    path = f'files/{folder_name}'
    if message.document:
        file = bot.get_file(message.document.file_id)
        download_file = bot.download_file(file.file_path)

        file_path = os.path.join(path, message.document.file_name)
        with open(file_path, "wb") as new_file:
            new_file.write(download_file)
        
        bot.send_message(message.chat.id, f"✅ Файл '{message.document.file_name}' збережено у {folder_name}")
    
    elif message.photo:
        file = bot.get_file(message.photo[-1].file_id) 
        download_file = bot.download_file(file.file_path)

        file_path = os.path.join(path, f"photo_{message.photo[-1].file_id}.jpg")
        with open(file_path, "wb") as new_file:
            new_file.write(download_file)
        
        bot.send_message(message.chat.id, f"✅ Файл '{message.document.file_name}' збережено у {folder_name}")

    else:
        bot.send_message(message.chat.id, "❌ Ви маєте надіслати файл або фото.")
        bot.register_next_step_handler(message, save_file_to_folder, folder_name)



# ==============
# Обробка кнопок
# ==============

@bot.callback_query_handler(func= lambda callback:True)
def callback_info(callback):

    # Інформація щодо навчання
    # ------------------------

    if callback.data == 'information':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Посилання на телеграм канали', callback_data='teleChats'))
        markup.add(types.InlineKeyboardButton('Файли з предметів', callback_data='files_folders'))
        bot.send_message(callback.message.chat.id,'Яку інформацію або матеріали ві бі хотіли отримати?', reply_markup=markup)

    elif callback.data == 'files_folders':
        markup = types.InlineKeyboardMarkup()
        for folder in os.listdir('files'):
            markup.add(types.InlineKeyboardButton(folder, callback_data=f'folders|{folder}'))
        bot.send_message(callback.message.chat.id, "Оберіть потрібний вам предмет:", reply_markup=markup)

    elif callback.data.startswith("folders|"):
        folder_name = callback.data.split("|", 1)[1]
        path = f'files/{folder_name}'
        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    bot.send_document(callback.message.chat.id, f)

    # Посилання на телеграм канали
    # ----------------------------

    elif callback.data == 'teleChats':
        with open("information/teleChats.json", "r", encoding="utf-8") as f:
            js = json.load(f)
            for i in js:
                bot.send_message(callback.message.chat.id, f"{i}:{js[i]}")

    # Інструменти адміна
    # ------------------

    elif callback.data == 'admin_tools':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Вимкнути бота', callback_data='shut_down'))
        markup.add(types.InlineKeyboardButton('Додати нову папку для предмету', callback_data='add_new_directory'))
        markup.add(types.InlineKeyboardButton('Додати вчитєля', callback_data='add_new_teacher'))
        markup.add(types.InlineKeyboardButton('додати адміна', callback_data='add_new_admin'))
        markup.add(types.InlineKeyboardButton('Вивести всі заявки до вчителів', callback_data='show_verification'))
        bot.send_message(callback.message.chat.id, "Який інструмент ви хочете використати?", reply_markup=markup)

    elif callback.data == 'shut_down':
        bot.stop_polling()

    elif callback.data == 'add_new_directory':
        bot.send_message(callback.message.chat.id, "Bведіть назву нової папки")
        bot.register_next_step_handler(callback.message, new_directory)

    elif callback.data == 'add_new_teacher':
        bot.send_message(callback.message.chat.id, "Bведіть id нового вчителя")
        bot.register_next_step_handler(callback.message, new_teacher)

    elif callback.data == 'add_new_admin':
        bot.send_message(callback.message.chat.id, "Bведіть id нового адміна")
        bot.register_next_step_handler(callback.message, new_admin)
        
    elif callback.data == 'show_verification':
        show_verification(callback.message)
    
    # Інструменти для вчителів
    # ------------------------
    elif callback.data == "teacher_tools":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Додати файл", callback_data='add_file'))
        markup.add(types.InlineKeyboardButton("Видалити файл", callback_data='delete_file'))
        markup.add(types.InlineKeyboardButton("Додати телегам канал", callback_data='add_telechat'))
        markup.add(types.InlineKeyboardButton("видалити телеграм каналь", callback_data='delete_telechat'))
        bot.send_message(callback.message.chat.id, "Оберіть дію", reply_markup=markup)

    elif callback.data == 'add_file':
        markup = types.InlineKeyboardMarkup()
        for folder in os.listdir('files'):
            markup.add(types.InlineKeyboardButton(folder, callback_data=f'folders_add|{folder}'))
        bot.send_message(callback.message.chat.id, "Оберіть потрібний вам предмет:", reply_markup=markup)
    
    elif callback.data == 'delete_file':
        markup = types.InlineKeyboardMarkup()
        for folder in os.listdir('files'):
            markup.add(types.InlineKeyboardButton(folder, callback_data=f'folders_delete|{folder}'))
        bot.send_message(callback.message.chat.id, "Оберіть потрібний вам предмет:", reply_markup=markup)

    elif callback.data.startswith('folders_add|'):
        folder_name = callback.data.split("|", 1)[1]
        path = f'files/{folder_name}'
        bot.send_message(callback.message.chat.id, f"📂 Ви обрали папку: {folder_name}\nТепер надішліть файл для збереження.")
        bot.register_next_step_handler(callback.message, save_file_to_folder, folder_name)
    


# ==============
# Обробка команд
# ==============

@bot.message_handler(commands=['start'])
def start_command(message):
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('/start'))

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Інформація', callback_data='information'))
    data = open_json('information/admins.json')
    user = str(message.from_user.id)

    if hashlib.md5(user.encode()).hexdigest() in data["admins_id"]:
        markup.add(types.InlineKeyboardButton("admin_tools", callback_data='admin_tools'))
    if hashlib.md5(user.encode()).hexdigest() in data["teachers_id"]:
        markup.add(types.InlineKeyboardButton("Інструменти для вчителів", callback_data='teacher_tools'))

    bot.send_message(message.chat.id, f'Вітаємо, {message.from_user.first_name} {message.from_user.last_name}, у боті Liceum. Оберіть дію.', reply_markup= markup)
    bot.send_message(message.chat.id,"⬇ Ви завжди можете перезапустити бота натиснувши /start",reply_markup=keyboard)

@bot.message_handler(commands=['info'])
def information(message):
    bot.send_message(message.chat.id, 'info')

@bot.message_handler(commands=['verification'])
def verify(message):
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    cur.execute("INSERT INTO ver (name, tg_id) VALUES (?, ?)", (full_name, message.from_user.id))
    con.commit()
    
    bot.send_message(message.chat.id, f"✅ {full_name}, вас успішно додано до бази!")


# ===========
# Запуск бота
# ===========

bot.polling(none_stop=True)
