import argparse
import bs4
import collections
import locale
import pymorphy2
import re
import requests

from datetime import datetime, timedelta, date
from nltk import pos_tag


def fetch_raw_html_from_habr(pages=10):
    habr_url = "https://habr.com/all/"
    for page in range(1, pages+1):
        page_url = '{}page{}'.format(habr_url, page)
        yield requests.get(page_url).text


def parse_habr_raw_htmls(raw_htmls):
    for raw_html in raw_htmls:
        soup = bs4.BeautifulSoup(raw_html, 'html.parser')
        articles = soup.find_all('article', {'class': 'post post_preview'})
        for article in articles:
            date = article.find("span", {"class": "post__time"}).text
            title = article.find('a', {"class": "post__title_link"}).text
            yield date, title


def arrange_nouns_by_weeks(articles_info):
    nouns_grouped_by_weeks = collections.defaultdict(list)
    for date, nouns in articles_info:
        week_number = date.isocalendar()[1]
        nouns_grouped_by_weeks[week_number].extend(nouns)
    return nouns_grouped_by_weeks


def get_first_and_last_week_days(year, week):
    first_day = date(year, 1, 1)
    if first_day.weekday() > 3:
        first_day += timedelta(7 - first_day.weekday())
    else:
        first_day -= timedelta(first_day.weekday())
    first_week_day = first_day + timedelta((week - 1) * 7)
    last_week_day = first_week_day + timedelta(days=6)
    return first_week_day, last_week_day


def print_most_frequent_nouns(frequent_nouns, top_words=3):
    print('-' * 80)
    format_string = '{:<15} | {:<15} | {}'
    print(format_string.format("Начало недели",
                               "Конец недели",
                               "Популярные слова",
                               )
          )
    print('-' * 80)
    for week in sorted(frequent_nouns):
        start, end = get_first_and_last_week_days(2018, week)
        nouns = collections.Counter(frequent_nouns[week])
        nouns = nouns.most_common(top_words)
        nouns_str = ', '.join(noun[0] for noun in nouns)
        print(format_string.format(str(start), str(end), nouns_str))
        print('-' * 80)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=int,
                        required=True,
                        help='number of pages to be parsed')
    parser.add_argument('--words', type=int,
                        default=3,
                        help='number of most frequent words to be found')
    return parser.parse_args()


def get_date_object(date_string, morphy):
    today = datetime.date(datetime.today())
    if 'сегодня' in date_string:
        return today
    elif 'вчера' in date_string:
        return today - timedelta(days=1)
    else:
        date = date_string.split()[:3]
        if not date[2].isdigit():
            date[2] = str(today.year)
            date[1] = morphy.parse(date[1])[0].normal_form
        return datetime.date(datetime.strptime(' '.join(date), '%d %B %Y'))


def get_normalized_nouns(title, morphy):
    title = title.lower()
    nouns = []
    for word in re.findall("[a-zа-я]+", title):
        p = morphy.parse(word)
        if 'NOUN' in p[0].tag:
            nouns.append(p[0].normal_form)
        elif 'LATN' in p[0].tag and pos_tag([word])[0][1] == 'NN':
            nouns.append(word)
    return nouns


def normalize(articles_info):
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    morphy = pymorphy2.MorphAnalyzer()
    for date_string, title in articles_info:
        date = get_date_object(date_string, morphy)
        nouns = get_normalized_nouns(title, morphy)
        yield date, nouns


if __name__ == '__main__':
    args = get_args()
    habr_raw_htmls = fetch_raw_html_from_habr(pages=args.pages)
    articles_info = parse_habr_raw_htmls(habr_raw_htmls)
    normalized_articles_info = normalize(articles_info)
    nouns_in_weeks = arrange_nouns_by_weeks(normalized_articles_info)
    print_most_frequent_nouns(nouns_in_weeks, top_words=3)
