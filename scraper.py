import download_settings as settings
from pathlib import Path
import itertools
import requests
import os


class Scraper:
    BASE_URL = 'https://www.cbr.ru/'

    def __init__(self):
        pass

    @staticmethod
    def get_files_names():
        return ['%s-%s%s01.rar' % tuple(r) for r in itertools.product(settings.FORMS, settings.YEARS, settings.MONTHS)]

    def check_downloads_folder(self):
        if os.path.exists(settings.PATH) and os.path.isdir(settings.PATH):
            files = [file for file in os.listdir(settings.PATH) if os.path.isfile('{}/{}'.format(settings.PATH, file))]
            server_files = self.get_files_names()
            result = sorted(files) == sorted(server_files)
            return True if result else os.rmdir(settings.PATH)
        return False

    def download_files(self):
        if self.check_downloads_folder(): return

        url = self.BASE_URL + 'vfs/credit/forms/'
        Path(settings.PATH).mkdir(parents=True, exist_ok=True)
        for file_name in self.get_files_names():
            link = url + file_name
            r = requests.get(link, allow_redirects=True)
            open('{}/{}'.format(settings.PATH, file_name), 'wb').write(r.content)
