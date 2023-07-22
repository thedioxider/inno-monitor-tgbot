import re
from datetime import datetime as dt
import requests
import lxml.html, lxml.etree


class Checker:
    PROGRAMS = [ 'DSAI', 'BCSE' ]
    URL = 'https://innopolis.university/sveden/apply/rating-of-applicants'
    PAYLOAD = {
        'type': 'enrolled',
        'education_type': 'ochno',
        'level-of-education': 'bachelors',
        'direction': '3',
        'financing_source': 'budget',
        'educational-program': '',
        'without_EGE': '',
        'date': ''
    }

    @staticmethod
    def get_page(url, payload):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        page = requests.get(url, headers=headers, params=payload)
        if not page.ok:
            return None
        return page

    def set_innoid(self, innoid):
        if re.fullmatch(r'[0-9- ]+', innoid) is not None:
            self.innoid = innoid.strip()
            return True
        else:
            return False

    def __init__(self, innoid='', program=0, noege=0):
        # uid: applicant's id or СНИЛС, as it appears in the table
        # program: 0 = dsai, 1 = bcse
        # noege: 0 for EGE results, 1 for БВИ, others for the rest quotas
        self.innoid = innoid
        self.program = program
        self.noege = noege
        self.score = -1
        self.hpos = 0  # highest position
        self.lpos = 0  # lowest position
        self.applicants = 0
        self.nullers = 0

    def upd_pos(self):
        self.score = -1
        self.hpos = 0
        self.lpos = 0
        self.applicants = 0
        self.nullers = 0
        payload = Checker.PAYLOAD.copy()
        payload['educational-program'] = Checker.PROGRAMS[self.program].lower()
        payload['without_EGE'] = self.noege
        upd_date = dt.today().strftime('%Y-%m-%d')
        payload['date'] = upd_date
        page = Checker.get_page(Checker.URL, payload)
        if page is None:
            raise requests.RequestException("Couldn't access the page")
        tree = lxml.html.fromstring(page.text)
        ### this xpath may change in future, idk
        tdata = tree.xpath('//section[@class="block-thirteen"]\
//section[contains(concat(" ",@class," ")," table-responsive ")]/table')
        if len(tdata) == 0:
            raise lxml.etree.ParseError("Couldn't access the data table")
        tdata = tdata[0]
        # self.applicants = 0
        # fdata = tdata.xpath('./tfoot/tr/td/b/text()')
        # if len(fdata) == 1:
        #     self.applicants = int(fdata[0])
        if self.noege == 0:
            eget = []
            for row in tdata.xpath('./tr'):
                d = row.xpath('./td/text()')
                egescore = int(d[4])+int(d[5])+ \
                           max(int(d[3]),int(d[6]))+int(d[7])
                if d[0] == self.innoid: self.score = egescore
                eget.append([d[0], egescore])
            eget = sorted(eget, key=lambda x: x[1], reverse=True)
            self.applicants = len(eget)
            self.nullers = 0
            for i, r in enumerate(eget):
                if r[1] == self.score:
                    if self.hpos == 0: self.hpos = i + 1
                    self.lpos = i + 1
                if self.is_nuller(score=r[1]): self.nullers += 1
        else:
            self.applicants = 0
            for row in tdata.xpath('./tr'):
                self.applicants += 1

    def is_nuller(self, score=None):
        if score is None: score = self.score
        return score <= 3
