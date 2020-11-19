from web_scraper import Scraper


def main():
    scraper = Scraper()
    r = scraper.find('1481')
    print(r)


if __name__ == '__main__':
    main()
