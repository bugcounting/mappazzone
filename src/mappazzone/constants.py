"""This module provides system-level paths of various resources used by the game."""

import os
from pathlib import Path

LANGUAGES = ['EN', 'IT']
ENV_LANGUAGE = 'ENV_LANGUAGE'

APP_NAME = 'mappazzone'

MAIN_DIR = os.path.abspath(os.path.dirname(__file__))

FLAGS_DIR = Path(MAIN_DIR, 'flags')

DATA_DIR = Path(MAIN_DIR, 'data')
CONTINENTS_PATH = Path(DATA_DIR, 'continents.csv')
CITIES_PATH = Path(DATA_DIR, 'worldcities.csv')
