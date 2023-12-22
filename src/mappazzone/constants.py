LANGUAGES = ['EN', 'IT']
ENV_LANGUAGE = 'ENV_LANGUAGE'

APP_NAME = 'mappazzone'

from pathlib import Path

MAIN_DIR = Path('src', 'mappazzone')

FLAGS_DIR = Path(MAIN_DIR, 'flags')

DATA_DIR = Path(MAIN_DIR, 'data')
CONTINENTS_PATH = Path(DATA_DIR, 'continents.csv')
CITIES_PATH = Path(DATA_DIR, 'worldcities.csv')
