import re
import requests
import lxml.html, lxml.etree


class Checker:
    PROGRAMS = [ 'dsai', 'bcse' ]
    URL = 'https://innopolis.university/sveden/apply/rating-of-applicants'
    PAYLOAD = {
        'type': 'enrolled',
        'education_type': 'ochno',
        'level-of-education': 'bachelors',
        'direction': '3',
        'financing_source': 'budget',
        'educational-program': '',
        'without_EGE': ''
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
            self.innoid = innoid
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
        self.position = 0
        self.applicants = 0
        self.nullers = 0
        self.upd_pos()

    def upd_pos(self):
        payload = Checker.PAYLOAD.copy()
        payload['educational-program'] = Checker.PROGRAMS[self.program]
        payload['without_EGE'] = self.noege
        page = Checker.get_page(Checker.URL, payload)
        if page is None:
            raise requests.RequestException("Couldn't access the page")
        # self.upd_date =

        tree = lxml.html.fromstring(page.text)
        # this xpath may change in future, idk
        tdata = tree.xpath('//section[@class="block-thirteen"]\
//section[contains(concat(" ",@class," ")," table-responsive ")]/table')
        if len(tdata) == 0:
            raise lxml.etree.ParseError("Couldn't access the data table")
        tdata = tdata[0]
        # self.applicants = 0
        # fdata = tdata.xpath('./tfoot/tr/td/b/text()')
        # if len(fdata) == 1:
        #     self.applicants = int(fdata[0])
        counter = 0
        nullers = 0
        for row in tdata.xpath('./tr'):
            counter += 1
            d = row.xpath('./td/text()')
            if d[0] == self.innoid:
                self.position = counter
            if int(d[1]) == 0:
                nullers += 1
        self.applicants = counter
        self.nullers = nullers
