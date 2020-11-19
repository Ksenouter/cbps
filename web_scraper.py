from requests_html import HTMLSession
import requests


class Scraper:

    BASE_URL = 'https://www.cbr.ru/banking_sector/credit/'

    def __init__(self):
        self.session = HTMLSession()

    def find(self, text):
        payload = {'find': text}
        url = self.BASE_URL + 'colist/'
        response = self.session.get(url, params=payload)
        results = response.html.find('tr')[1:]
        return results

    def find_bank_url(self, reg_num, name):
        results = self.find(reg_num)
        if len(results) < 1:
            return None
