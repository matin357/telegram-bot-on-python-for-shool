import telebot
file_with_tocken = open("tocken.txt", "r")
tocken = file_with_tocken.readlines(1)
bot = telebot.TeleBot(f'{tocken[0]}')

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'Вітаємо у боті Liceum. Оберіть дію.')



bot.polling(none_stop=True)
