import telebot
from checker import Checker


class User:
    def __init__(self, uid):
        self.uid = uid
        self.checker = Checker()
        self.bvi = Checker()
        self.bvi.noege = 1


ulist = {}

API_TOKEN = ''
with open('TOKEN.txt') as f:
    API_TOKEN = f.readline()
bot = telebot.TeleBot(API_TOKEN)


def register_step(inpt, uid):
    if ulist[uid].checker.set_innoid(inpt.text.strip()):
        cb_program = telebot.util.quick_markup({
            'DSAI': {'callback_data': f'cb_program 0'},
            'BCSE': {'callback_data': f'cb_program 1'}
        })
        bot.send_message(inpt.chat.id, "Please, choose your educational program:", reply_markup=cb_program)
    else:
        rep = bot.reply_to(inpt, "Wrong ID format. Please, enter it correctly:")
        bot.register_next_step_handler(rep, register_step)


@bot.message_handler(commands=['start'])
def start_bot(msg):
    u = msg.from_user
    ulist[u.id] = User(u.id)
    rep = bot.send_message(msg.chat.id,
"Hi! Here you can get actual info about your position in the list of Innopolis University applicants.\
\n\nPlease, enter your applicant ID as it's displayed in the table (you can also find it in your personal account):")
    bot.register_next_step_handler(rep, register_step, u.id)


@bot.callback_query_handler(func=lambda call: True)
def answer_query(call):
    cbdata = call.data.split(' ')
    if cbdata[0] == 'cb_program':
        u = call.from_user
        ulist[int(u.id)].checker.program = int(cbdata[1])
        ulist[int(u.id)].bvi.program = int(cbdata[1])
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Complete! Now you can check your position by entering /position")
    print(f'Registred {u.first_name} (@{u.username})[{u.id}]')


@bot.message_handler(commands=['position'])
def get_position(msg):
    if msg.from_user.id not in ulist.keys():
        bot.send_message(msg.chat.id, "Seems like you're not registered yet. Maybe bot has been rebooted since your last visit. Please, use /start to register")
        return
    uc = ulist[msg.from_user.id].checker
    ub = ulist[msg.from_user.id].bvi
    uc.upd_pos()
    ub.upd_pos()
    bot.send_message(msg.chat.id,
f"Your position now is:\n*{uc.position+ub.applicants} of {uc.applicants-uc.nullers+ub.applicants}* (_{ub.applicants}_ are without entrance test -- _БВИ_).\n\
There are also {uc.nullers} people yet without EGE score in table ({uc.applicants} total).",
parse_mode='markdown')


print('\nOnline!')
bot.infinity_polling()
