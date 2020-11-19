from scraper import Scraper


def main():
    scraper = Scraper()
    scraper.download_files()
    scraper.extract_downloads()


if __name__ == '__main__':
    main()
