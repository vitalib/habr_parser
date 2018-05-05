#  Habrhabr titles's statistics analyzer

Prints most frequent normalized nouns in habr post's titles for last n pages.

## Getting Started

Script should be run by Python3.5 and higher. 

### Prerequisites

Dependencies should be installed as follows:
```bash
pip install -r requirements.txt
```

### Exampale of running

```bash
python3 habr_stat.py --pages 40
--------------------------------------------------------------------------------
Начало недели   | Конец недели    | Популярные слова
--------------------------------------------------------------------------------
2018-04-16      | 2018-04-22      | апрель, дайджест, материал
--------------------------------------------------------------------------------
2018-04-23      | 2018-04-29      | часть, система, управление
--------------------------------------------------------------------------------
2018-04-30      | 2018-05-06      | часть, безопасность, система
--------------------------------------------------------------------------------

```
## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

