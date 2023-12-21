from typing import Set, List
import logging
from dataclasses import dataclass
from enum import Enum
from collections import UserList
import os
import csv
import sys
import re
import random

from constants import ENV_LANGUAGE, CONTINENTS_PATH, CITIES_PATH


class Direction(Enum):
    LATITUDE = 'latitude'
    LONGITUDE = 'longitude'


class Continent_(Enum):

    def __repr__(self) -> str:
        return self.__class__.__name__ + '.' + self.name

class ContinentEN(Continent_):
    AN = "Antarctica"
    AS = "Asia"
    AF = "Africa"
    EU = "Europe"
    NA = "North America"
    OC = "Oceania"
    SA = "South America"

class ContinentIT(Continent_):
    AN = "Antartide"
    AS = "Asia"
    AF = "Africa"
    EU = "Europa"
    NA = "Nordamerica"
    OC = "Oceania"
    SA = "Sudamerica"


if os.environ[ENV_LANGUAGE] == 'EN':
    Continent = ContinentEN
elif os.environ[ENV_LANGUAGE] == 'IT':
    Continent = ContinentIT


@dataclass(unsafe_hash=True)
class Location:
    city: str
    city_ascii: str
    longitude: float
    latitude: float
    country: str
    country_iso2: str
    country_iso3: str
    population: int
    identifier: int
    continent: Continent
    capital: bool = False

    def before(self, other, direction: Direction, tolerance: float) -> bool:
        """
        If `direction` is LONGITUDE: is `self.longitude` less than `other.longitude`?
        If `direction` is LATITUDE: is `self.latitude` greater than `other.latitude`?
        Both are evaluate within `tolerance` degrees.
        """
        if direction == Direction.LONGITUDE:
            return (self.longitude < other.longitude or
                    self.longitude - other.longitude <= tolerance)
        elif direction == Direction.LATITUDE:
            return (self.latitude > other.latitude or
                    other.latitude - self.latitude <= tolerance)


class Locations(UserList):

    # If `load`, `content` is ignored and a local list of locations is loaded
    def __init__(self, content=[], load: bool=False):
        if load:
            content = self._load()
        super().__init__(content)

    def keep(self, capitals_only: bool, continents: Set[Continent]):
        """Keep only locations that satisfy criteria."""
        # Filter according to options
        filtered_data = [loc for loc in self.data if (
            (loc.capital or not capitals_only) and
            (loc.continent in continents)
        )]
        self.data = filtered_data

    def pick(self, k=1) -> List[Location]:
        """Return a list with `k` random locations and remove them from `self`.
        If there are fewer than `k` elements in `self`, raise ValueError."""  
        if k > len(self.data):
            raise ValueError(f'Not enough locations available: {k} > {len(self.data)}')
        indexes = random.sample(range(len(self.data)), k)
        result = [self[k] for k in indexes]
        # Remove in reverse order, so we don't have to recompute indexes
        for index in sorted(indexes, reverse=True):
            del self[index]
        return result

    def get(self, city:str) -> Location:
        """Return location given its city name."""
        for location in self.data:
            if location.city == city:
                return location
        raise ValueError(f'City {city} not found')

    @classmethod
    def _load(cls) -> Set:
        logger = logging.getLogger(__name__)
        locations = []
        country_to_continent = {}
        with open(CONTINENTS_PATH, mode='r', newline='', encoding='utf-8') as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                country, continent, code = row['iso3'], row['continent'], row['code']
                continent = [c for c in Continent if c.name == code]
                assert len(continent) == 1, f'Continent with code {code} not found'
                continent = continent[0]
                country_to_continent[country] = continent
        with open(CITIES_PATH, mode='r', newline='', encoding='utf-8') as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                city = row['city']
                city_ascii = row['city_ascii']
                latitude = float(row['lat'])
                longitude = float(row['lng'])
                country = row['country']
                iso2 = row['iso2']
                iso3 = row['iso3']
                capital = row['capital'] == 'primary'
                try:
                    population = int(row['population'])
                except ValueError:
                    logger.debug(f'Population of: {iso3} ({city}) not found')
                    population = 0
                identifier = int(row['id'])
                try:
                    continent = country_to_continent[iso3]
                except KeyError:
                    logger.debug(f'Continent of: {iso3} ({city}) not found')
                    continent = None
                if continent:
                    country = re.sub(r'[(].*[)]', '', country).strip()
                    location = Location(city=city, city_ascii=city_ascii,
                                        longitude=longitude, latitude=latitude,
                                        country=country, population=population,
                                        identifier=identifier,
                                        country_iso2=iso2,
                                        country_iso3=iso3,
                                        continent=continent, capital=capital)
                    locations.append(location)
        return set(locations)
