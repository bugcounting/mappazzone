import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')

from mappazzone.constants import ENV_LANGUAGE
os.environ[ENV_LANGUAGE] = 'EN'
from mappazzone.locations import Continent, Direction, Location, Locations


class TestLocation:

    def test_before_longitude(self):
        loc1 = Location('C1', '', 10, 0, 'country', '', '', 0, 1, Continent.EU)
        loc2 = Location('C2', '', 20, 0, 'country', '', '', 0, 1, Continent.EU)
        assert loc1.before(loc2, Direction.LONGITUDE, tolerance=0.0)
        assert loc1.before(loc1, Direction.LONGITUDE, tolerance=0.0)
        assert loc2.before(loc1, Direction.LONGITUDE, tolerance=10.0)
        assert not loc2.before(loc1, Direction.LONGITUDE, tolerance=1.0)
        assert not loc2.before(loc1, Direction.LONGITUDE, tolerance=0.0)
        loc3 = Location('C3', '', -30, 0, 'country', '', '', 0, 1, Continent.EU)
        assert loc3.before(loc1, Direction.LONGITUDE, tolerance=0.0)
        assert loc3.before(loc2, Direction.LONGITUDE, tolerance=0.0)
        assert not loc2.before(loc3, Direction.LONGITUDE, tolerance=0.0)
        assert not loc1.before(loc3, Direction.LONGITUDE, tolerance=0.0)
        loc4 = Location('C4', '', -40, 0, 'country', '', '', 0, 1, Continent.EU)
        assert loc4.before(loc3, Direction.LONGITUDE, tolerance=0.0)
        assert loc3.before(loc4, Direction.LONGITUDE, tolerance=15.0)
        assert not loc3.before(loc4, Direction.LONGITUDE, tolerance=1.0)

    def test_before_latitude(self):
        loc1 = Location('C1', '', 0, 10, 'country', '', '', 0, 1, Continent.EU)
        loc2 = Location('C2', '', 0, 20, 'country', '', '', 0, 1, Continent.EU)
        assert not loc1.before(loc2, Direction.LATITUDE, tolerance=0.0)
        assert loc1.before(loc1, Direction.LATITUDE, tolerance=0.0)
        assert loc2.before(loc1, Direction.LATITUDE, tolerance=10.0)
        assert loc2.before(loc1, Direction.LATITUDE, tolerance=1.0)
        assert loc2.before(loc1, Direction.LATITUDE, tolerance=0.0)
        loc3 = Location('C3', '', 0, -30, 'country', '', '', 0, 1, Continent.EU)
        assert loc1.before(loc3, Direction.LATITUDE, tolerance=0.0)
        assert loc2.before(loc3, Direction.LATITUDE, tolerance=0.0)
        assert not loc3.before(loc2, Direction.LATITUDE, tolerance=0.0)
        assert not loc3.before(loc1, Direction.LATITUDE, tolerance=0.0)
        loc4 = Location('C4', '', 0, -40, 'country', '', '', 0, 1, Continent.EU)
        assert loc3.before(loc4, Direction.LATITUDE, tolerance=0.0)
        assert loc4.before(loc3, Direction.LATITUDE, tolerance=15.0)
        assert not loc4.before(loc3, Direction.LATITUDE, tolerance=1.0)


class TestLocations:

    def locations(self):
        return [
            Location('EU', '', 10, 0, 'country', '', '', 0, 1, Continent.EU, True),
            Location('EU2', '', -10, 0, 'country', '', '', 0, 1, Continent.EU, False),
            Location('AN', '', 10, 0, 'country', '', '', 0, 1, Continent.AN, True),
            Location('AN2', '', 20, 0, 'country', '', '', 0, 1, Continent.AN, False),
            Location('AS', '', 10, 30, 'country', '', '', 0, 1, Continent.AS, True),
            Location('AS2', '', 20, 40, 'country', '', '', 0, 1, Continent.AS, False),
            Location('NA', '', 10, 30, 'country', '', '', 0, 1, Continent.NA, True),
            Location('NA2', '', 20, 40, 'country', '', '', 0, 1, Continent.NA, False),
            Location('SA', '', 90, -30, 'country', '', '', 0, 1, Continent.SA, True),
            Location('SA2', '', 20, -40, 'country', '', '', 0, 1, Continent.SA, False),
            Location('OC', '', -90, -30, 'country', '', '', 0, 1, Continent.OC, True),
            Location('OC2', '', -20, -40, 'country', '', '', 0, 1, Continent.OC, False),
            Location('AF', '', 10, 30, 'country', '', '', 0, 1, Continent.AF, True),
            Location('AF2', '', 20, 40, 'country', '', '', 0, 1, Continent.AF, False)
        ]

    def test_keep(self):
        for continent in Continent:
            locs = Locations(content=self.locations())
            locs.keep(capitals_only=False, continents=set([continent]))
            assert len(locs) == 2
        locs = Locations(content=self.locations())
        locs.keep(capitals_only=True, continents=[])
        assert len(locs) == 0
        locs = Locations(content=self.locations())
        len_locs = len(locs)
        locs.keep(capitals_only=False, continents=list(Continent))
        assert len(locs) == len_locs
        locs = Locations(content=self.locations())
        locs.keep(capitals_only=True, continents=list(Continent))
        assert len(locs) == len_locs // 2

    def test_pick(self):
        locs = Locations(content=self.locations())
        len_locs = len(locs)
        locs.pick()
        assert len(locs) == len_locs - 1
        len_locs = len(locs)
        locs.pick(3)
        assert len(locs) == len_locs - 3
        
    def test_get(self):
        locs = Locations(content=self.locations())
        assert locs.get('NA')
        assert locs.get('EU2')
        with pytest.raises(ValueError) as ex:
            locs.get('Paris')
