import download_settings as settings
from pyunpack import Archive
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
            files = [file for file in os.listdir(settings.PATH)]
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

    def check_files_folder(self):
        if os.path.exists(settings.FILES_PATH) and os.path.isdir(settings.FILES_PATH):
            dirs = [dir for dir in os.listdir(settings.FILES_PATH)]
            server_dirs = [file[:-4] for file in self.get_files_names()]
            result = sorted(dirs) == sorted(server_dirs)
            return True if result else os.rmdir(settings.FILES_PATH)
        return False

    def extract_downloads(self):
        if not self.check_downloads_folder(): return False
        if self.check_files_folder(): return True

        Path(settings.FILES_PATH).mkdir(parents=True, exist_ok=True)
        for file in os.listdir(settings.PATH):
            rar_file_path = '{}/{}'.format(settings.PATH, file)
            if not os.path.isfile(rar_file_path): continue
            extract_path = '{}/{}'.format(settings.FILES_PATH, file[:-4])
            Path(extract_path).mkdir(parents=True, exist_ok=True)
            Archive(rar_file_path).extractall(extract_path)
        return True
