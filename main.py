from scraper import Scraper
from dbf_parser import Parser


def main():
    scraper = Scraper()
    scraper.download_files(reload=False)
    scraper.extract_downloads()
    Parser.pars_forms(recreate_sources=False)


if __name__ == '__main__':
    main()
