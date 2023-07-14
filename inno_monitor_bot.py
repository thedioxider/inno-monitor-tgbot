import requests
from lxml import html

class Checker:
    PROGRAMS = [ 'dsai', 'bcse' ]
    URL = 'https://innopolis.university/sveden/apply/rating-of-applicants'
    PLOAD = {
        'type':'enrolled',
        'education_type':'ochno',
        'level-of-education':'bachelors',
        'direction':'3',
        'financing_source':'budget'
    }
    
    @staticmethod
    def getPage(url, payload):
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        page = requests.get(url, headers=headers, params=payload)
        if not page.ok:
            return None
        return page
    
    
    def __init__(self, uid, program=0, noege=0):
        # uid: applicant's id or СНИЛС, as it appears in the table
        # program: 0 = dsai, 1 = bcse
        # noege: 0 for EGE results, 1 for БВИ, others for the rest quotas
        self.uid = uid
        self.program = program
        self.noege = noege
        self.updPos()
    
    def updPos(self):
        pload = Checker.PLOAD.copy()
        pload['educational-program'] = Checker.PROGRAMS[self.program]
        pload['without_EGE'] = self.noege
        page = Checker.getPage(Checker.URL, pload)
        if page == None:
            raise requests.RequestException("Couldn't access the page")
        #self.upd_date =
        
        tree = html.fromstring(page.text)
        # this xpath may change in future, idk
        tdata = tree.xpath('//section[@class="block-thirteen"]//section[contains(concat(" ",@class," ")," table-responsive ")]/table')
        if len(tdata) == 0:
            raise lxml.etree.ParseError("Couldn't access the data table")
        tdata = tdata[0]
        #self.applicants = 0
        #fdata = tdata.xpath('./tfoot/tr/td/b/text()')
        #if len(fdata) == 1:
        #    self.applicants = int(fdata[0])
        self.position = 0
        counter = 0
        nullers = 0
        for row in tdata.xpath('./tr'):
            counter += 1
            d = row.xpath('./td/text()')
            if d[0] == self.uid:
                self.position = counter
            if int(d[1]) == 0:
                nullers += 1
        self.applicants = counter
        self.nullers = nullers


import telebot

class User:
    def __init__(self, uid):
        self.uid = uid
        self.has_data = False
        self.wait_for = -1

ulist = {}

API_TOKEN = ''
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start','help'])
def start_bot(msg):
    user = msg.from_user
    ulist[user.id] = User(user.id)
    bot.reply_to(msg, "hellooo hiiiii ohayo yooooo")
    print(f'Registred {user.first_name} (@{user.username})[{user.id}]')


print('\nOnline!')
bot.infinity_polling()
