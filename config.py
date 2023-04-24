import os

BOT_TOKEN: str = "6035269729:AAFGOP4pHyaqf2OXUKtrDSS6wLEtMZ4Qy28"

ROOT_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(ROOT_DIR, 'logs')
DATABASE_PATH = os.path.join(ROOT_DIR, 'database.sqlite')

TOTAL_MARKS = [i for i in range(1, 11)]

SEARCH_CITY_INLINE_QUERY = '🔎 Поиск города: '
SEARCH_GENDER_INLINE_QUERY = '🔎 Выбрать пол: '