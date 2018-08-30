import bs4
import itertools
import locale
import pymorphy2
import requests

from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def get_date_object(date_string, pymorphy):
    today = datetime.date(datetime.today())
    if 'сегодня' in date_string:
        return today
    elif 'вчера' in date_string:
        return today - timedelta(days=1)
    else:
        date = date_string.split()[:3]
        if not date[2].isdigit():
            date[2] = str(today.year)
            date[1] = pymorphy.parse(date[1])[0].normal_form
        return datetime.date(datetime.strptime(' '.join(date), '%d %B %Y'))


def _fetch_raw_html(url):
    return requests.get(url).text


def fetch_raw_htmls_from_habr(pages=10):
    habr_url = "https://habr.com/all/"
    pages_urls = ('{}page{}'.format(habr_url, page)
                  for page in range(1, pages+1))
    with ThreadPoolExecutor(max_workers=25) as executor:
        raw_htmls = executor.map(_fetch_raw_html, pages_urls)
    return raw_htmls


def parse_habr_raw_html(raw_html):
    soup = bs4.BeautifulSoup(raw_html, 'html.parser')
    articles = soup.find_all('article', {'class': 'post post_preview'})
    articles_info = []
    pymorphy = pymorphy2.MorphAnalyzer()
    for article in articles:
        date = article.find("span", {"class": "post__time"}).text
        date_object = get_date_object(date, pymorphy)
        title = article.find('a', {"class": "post__title_link"}).text
        articles_info.append((date_object, title))
    return articles_info


def parse_habr_raw_htmls(raw_htmls):
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    with ProcessPoolExecutor() as executor:
        articles_infos = executor.map(parse_habr_raw_html, raw_htmls)
    return itertools.chain(*articles_infos)
