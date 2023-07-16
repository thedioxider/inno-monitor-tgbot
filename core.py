import telebot
from checker import Checker


class User:
    def __init__(self, uid):
        self.uid = uid

ulist = {}

API_TOKEN = ''
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def start_bot(msg):
    user = msg.from_user
    ulist[user.id] = User(user.id)
    bot.reply_to(msg, "hellooo hiiiii ohayo yooooo")
    print(f'Registred {user.first_name} (@{user.username})[{user.id}]')


print('\nOnline!')
bot.infinity_polling()
