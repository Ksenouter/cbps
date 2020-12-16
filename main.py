from scraper import Scraper
from dbf_parser import Parser


def main():
    scraper = Scraper()
    scraper.download_files()
    scraper.extract_downloads()
    Parser.pars_forms()


if __name__ == '__main__':
    main()
