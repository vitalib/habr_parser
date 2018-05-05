import argparse
import collections
import re
from datetime import timedelta, date

import pymorphy2
from nltk import pos_tag

from habr_pars import fetch_raw_htmls_from_habr, parse_habr_raw_htmls


def arrange_nouns_by_weeks(articles_info):
    nouns_grouped_by_weeks = collections.defaultdict(list)
    for date, nouns in articles_info:
        week_number = date.isocalendar()[1]
        nouns_grouped_by_weeks[week_number].extend(nouns)
    return nouns_grouped_by_weeks


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=int,
                        required=True,
                        help='number of pages to be parsed')
    parser.add_argument('--words', type=int,
                        default=3,
                        help='number of most frequent words to be found')
    return parser.parse_args()


def get_first_and_last_week_dates(week, year=2018):
    first_day = date(year, 1, 1)
    if first_day.weekday() > 3:
        first_day += timedelta(7 - first_day.weekday())
    else:
        first_day -= timedelta(first_day.weekday())
    first_week_day = first_day + timedelta((week - 1) * 7)
    last_week_day = first_week_day + timedelta(days=6)
    return first_week_day, last_week_day


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
    morphy = pymorphy2.MorphAnalyzer()
    for date_object, title in articles_info:
        nouns = get_normalized_nouns(title, morphy)
        yield date_object, nouns


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
        start, end = get_first_and_last_week_dates(week, year=2018)
        nouns = collections.Counter(frequent_nouns[week])
        nouns = nouns.most_common(top_words)
        nouns_str = ', '.join(noun[0] for noun in nouns)
        print(format_string.format(str(start), str(end), nouns_str))
        print('-' * 80)


if __name__ == '__main__':
    args = get_args()
    habr_raw_htmls = fetch_raw_htmls_from_habr(pages=args.pages)
    articles_info = parse_habr_raw_htmls(habr_raw_htmls)
    normalized_nouns_in_articles = normalize(articles_info)
    nouns_in_weeks = arrange_nouns_by_weeks(normalized_nouns_in_articles)
    print_most_frequent_nouns(nouns_in_weeks, top_words=3)
