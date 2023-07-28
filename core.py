import sys
from datetime import datetime as dt
import telebot
from checker import Checker


CREATE_LOGS = False
if CREATE_LOGS:
    log_file = 'bot.log'
    log_output = None
    try:
        log_output = open(log_file, 'x').close()
        log_output = open(log_file, 'a')
    except FileExistsError:
        log_output = open(log_file, 'a')
        print('\n', file=log_output)
    # sys.stderr = open('bot.err', 'a')


def log(entry):
    print(f'{dt.today().strftime("[%Y-%m-%d %H:%M:%S]")} ' + str(entry))
    if CREATE_LOGS:
        print(f'{dt.today().strftime("[%Y-%m-%d %H:%M:%S]")} ' + str(entry),
              file=log_output)
        log_output.flush()


class User:
    def __init__(self, uid):
        self.uid = uid
        self.checker = Checker()
        self.bvi = Checker()
        self.bvi.noege = 1


ulist = {}

API_TOKEN = ''
with open('TOKEN.txt') as f:
    API_TOKEN = f.readline().strip()
bot = telebot.TeleBot(
    API_TOKEN,
    parse_mode='html'
)


def register_innoid_step(inpt, u, tries=0):
    if ulist[u.id].checker.set_innoid(inpt.text.strip()):
        log(f'Registered {u.first_name} (@{u.username})<{u.id}>')
        register_program_step(u, inpt.chat)
    elif inpt.text[0] == '/':
        bot.clear_step_handler_by_chat_id(inpt.chat.id)
    elif tries < 2:
        rep = bot.reply_to(inpt, "Wrong ID format. Please, enter it correctly or /cancel:")
        bot.register_next_step_handler(rep, register_innoid_step, u, tries+1)
    else:
        rep = bot.reply_to(inpt, "Wrong ID format")


def register_program_step(u, chat):
    cb_program = telebot.util.quick_markup({
        'DSAI': { 'callback_data': 'program 0' },
        'BCSE': { 'callback_data': 'program 1' },
        'Cross Table': { 'callback_data': 'program -1' }
    }, row_width = 2)
    bot.send_message(chat.id, "Please, choose your educational program:",
                     reply_markup=cb_program)


@bot.message_handler(commands=['start'])
def start_bot(msg):
    u = msg.from_user
    ulist[u.id] = User(u.id)
    rep = bot.send_message(msg.chat.id,
"Hi! Here you can get actual info about your position in the list of Innopolis University applicants.\
\n\nPlease, enter your <u><i>applicant ID</i></u> (you can find it in your personal account) or <u><i>СНИЛС number</i></u> \
(if you registered on gosuslugi.ru) as it's displayed in the table:")
    bot.register_next_step_handler(rep, register_innoid_step, u)


@bot.message_handler(commands=['help'])
def help_info(msg):
    bot.send_message(msg.chat.id,
"This bot is made\n\
by @theDioxider [ <a href='https://github.com/thedioxider/inno-monitor-tgbot/'>GitHub</a> ]\n\
All information is taken from the <a href='https://innopolis.university/sveden/apply/rating-of-applicants?type=enrolled'>Innopolis Ratings of applicants</a>\n\n\
\U0001f90d Wish you luck with entering the University",
disable_web_page_preview=True)


@bot.message_handler(commands=['position'])
def get_position(msg, u=None):
    if u is None: u = msg.from_user
    if u.id not in ulist.keys():
        bot.send_message(msg.chat.id,
"Seems like you're not registered yet. Maybe bot has been rebooted since your last visit.\n\
Please, use /start to register")
        return
    loadmsg = bot.send_message(msg.chat.id, "<i>loading...</i>")
    uc = ulist[u.id].checker
    ub = ulist[u.id].bvi
    uc.upd_pos()
    ub.upd_pos()
    report = f"<u><i>{dt.today().strftime('%d %B')} \
[{'Cross' if uc.program == -1 else Checker.PROGRAMS[uc.program]}]:</i></u>\n"
    if uc.hpos == 0 or uc.lpos == 0:
        report += "Seems like you are not in the list yet. Maybe you have entered wrong ID. \
You can try entering <i>СНИЛС</i> instead of <i>applicant ID</i>, or vice versa. \
Please, try again: /start\n\
If you think, there was a mistake, please, contact @theDioxider\n"
    elif uc.is_nuller():
        report += "Your EGE score is not filled yet. \
Position is unavailable. Please, check it later\n"
    elif uc.hpos == uc.lpos:
        report += f"Your position (<u>including</u> applicants with БВИ):\n\
<b><i>{uc.lpos+ub.applicants} of {uc.applicants+ub.applicants}</i></b>\n"
    else:
        report += f"There are several applicants with the same EGE score as you. \
Your position (<u>including</u> applicants with БВИ, who <i><u>have already brought the originals</u></i>) is in range:\n\
<b><i>{uc.hpos+ub.origs}-{uc.lpos+ub.origs} of {uc.applicants+ub.origs}</i></b>\n"
    report += f"\n<i>{ub.applicants} are with БВИ ({ub.origs} brought originals), {uc.nullers} are with 0 EGE score\n\
({uc.applicants+ub.applicants} in total)</i>\n\
Refresh with /position or using the button below"
    markup = {}
    if uc.program != -1:
        markup['Online Table'] = { 'url': f'{uc.turl}' }
    markup['Refresh'] = { 'callback_data': f'refresh {uc.program}' }
    cb_refresh = telebot.util.quick_markup(markup)
    bot.delete_message(loadmsg.chat.id, loadmsg.id)
    bot.send_message(
        msg.chat.id,
        report,
        reply_markup=cb_refresh,
        disable_web_page_preview=True
    )


@bot.callback_query_handler(func=lambda call: True)
def answer_query(call):
    cbdata = call.data.split(' ')
    u = call.from_user
    if cbdata[0] in ['program','refresh']:
        if u.id not in ulist.keys():
            bot.send_message(call.message.chat.id,
"This session is outdated.\n\
Please, register again: /start")
            return
        ulist[u.id].checker.program = int(cbdata[1])
        ulist[u.id].bvi.program = int(cbdata[1])
        if cbdata[0] == 'program':
            bot.answer_callback_query(call.id, "Complete registration!")
            get_position(call.message, u)
        elif cbdata[0] == 'refresh':
            bot.delete_message(call.message.chat.id, call.message.id)
            get_position(call.message, u)


log('Online!')
bot.infinity_polling()
