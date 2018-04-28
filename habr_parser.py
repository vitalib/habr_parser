import argparse
import requests
import locale
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
import pymorphy2
from collections import defaultdict, Counter


def normalize_date(morph_analyzer, date_string):
    return morph_analyzer.parse(date_string)[0].normal_form


def get_normalized_noun(morph_analyzer, word):
    p = morph_analyzer.parse(word)
    if p and 'NOUN' in p[0].tag:
        return p[0].normal_form
    return None

def date_str_to_datetime_object(date):
    today = datetime.date(datetime.now())
    yesterday = today - timedelta(days=1)
    date_format = '%d %B %Y'
    if 'сегодня' in date:
        date = today
    elif 'вчера' in date:
        date = yesterday
    else:
        date = datetime.date(datetime.strptime(date, date_format))
    return date


def normalize_nouns(titles):
    morph = pymorphy2.MorphAnalyzer()
    nouns_normalized = []
    for title in titles:
        nouns_from_title = []
        for word in title.split():
            noun = get_normalized_noun(morph, word)
            if noun:
                nouns_from_title.append(noun)
        nouns_normalized.append(nouns_from_title)
    return nouns_normalized



def modify_dates(dates):
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    morph = pymorphy2.MorphAnalyzer()
    modified_dates = []
    for date in dates:
        date = date.split()[:2]# ['сегодня', 'в'] или ['24', 'апреля']
        date[-1] = normalize_date(morph, date[-1])# апреля = апрель, марта = март
        date.append('2018')
        datetime_obj = date_str_to_datetime_object(' '.join(date))
        modified_dates.append(datetime_obj)
    return modified_dates


def parse_habr(url, pages=1):
    dates_headers = []
    for page in range(1, pages+1):
        print('Processing page {}'.format(page))
        page_url = '{}page{}/'.format(url, page)
        page_response = requests.get(page_url)
        soup = BeautifulSoup(page_response.text, 'html.parser')
        dates = soup.find_all("span", {"class": "post__time"})
        titles = soup.find_all('a', {"class": "post__title_link"})
        dates = [date.string for date in dates]
        dates = modify_dates(dates)
        titles = [title.string for title in titles]
        nouns_of_titles = normalize_nouns(titles)
        dates_headers.extend(list(zip(dates, nouns_of_titles)))
    return dates_headers


def select_nouns_from_headers(dates_headers_dict):
    pass



def get_dates_header_dict(headers_dates):
    dates_headers = defaultdict(list)
    for date, nouns in headers_and_dates:
        dates_headers[date].extend(nouns)
    return dates_headers


def frequent_nouns(dates_dict, top_size=3):
    dates_frequent = defaultdict(list)
    for date, nouns in dates_dict.items():
        dates_frequent[date] = Counter(nouns).most_common(top_size)
    return dates_frequent


def get_most_frequent_by_weeks(dates_dict):
    result_dict = defaultdict(list)
    for day, nouns in dates_dict.items():
        result_dict[day.isocalendar()[1]].extend(nouns)
    return result_dict


def get_first_and_last_week_days(year, week):
    first_day = date(year, 1, 1)
    if first_day.weekday() > 3:
        first_day += timedelta(7 - first_day.weekday())
    else:
        first_day -= timedelta(first_day.weekday())
    first_week_day = first_day + timedelta((week - 1) * 7)
    last_week_day = first_week_day + timedelta(days=6)
    return first_week_day, last_week_day



def print_frequent(frequent, top_words):
    for week, nouns in frequent.items():
        print(get_first_and_last_week_days(2018, week),
              Counter(nouns).most_common(top_words))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=int,
                        required=True,
                        help='number of pages to be parsed')
    parser.add_argument('--words', type=int,
                       default=3,
                       help='number of most frequent words to be found')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    habr_url = "https://habr.com/all/"
    headers_and_dates = parse_habr(habr_url, args.pages)
    dates_headers_dict = get_dates_header_dict(headers_and_dates)
    frequent = get_most_frequent_by_weeks(dates_headers_dict)
    print_frequent(frequent, args.words)
    """
    nouns_from_header_in_dates = select_nouns_from_headers(headers_in_dates)   
    normalized_nouns_in_dates = normalize_nouns(nouns_from_header_in_dates)
    nouns_grouped_by_weeks = group_nouns_by_week(normalized_nouns_in_dates)
    frequent_nouns_by_weeks = get_frequent_nouns(nouns_from_header_in_dates,
                                                 words)
    """
