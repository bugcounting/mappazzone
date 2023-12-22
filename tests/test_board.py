import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')

from mappazzone.constants import ENV_LANGUAGE
os.environ[ENV_LANGUAGE] = 'EN'
from mappazzone.locations import Continent, Direction, Location
from mappazzone.board import Board


class TestBoard:

    def test_init(self):
        center = Location('center', '', 0, 0, 'country', 'iso2', 'iso3', 0, 0,
                          Continent.EU)
        board = Board(center, Board.BoardOptions(10))
        assert len(board.grid) == board.size
        assert len(board.grid[0]) == board.size
        assert board.get_center() == center
        assert board.grid[board.center_x][board.center_y] == center

    def test_no_violations(self):
        center = Location('center', '', 0, 0, 'country', 'iso2', 'iso3', 0, 0,
                          Continent.AS)
        board = Board(center, Board.BoardOptions(10))
        assert board.center_x == 5 and board.center_y == 5
        assert not board.violations()
        n = Location('N', '', 0, 50, 'country', 'iso2', 'iso3', 0, 0, Continent.EU)
        board.put(n, *board.coords(0, -4, centered=True))
        assert not board.violations()
        s = Location('S', '', 0, -50, 'country', 'iso2', 'iso3', 0, 0, Continent.AF)
        board.put(s, *board.coords(0, 4, centered=True))
        assert not board.violations()
        e = Location('E', '', 50, 0, 'country', 'iso2', 'iso3', 0, 0, Continent.OC)
        board.put(e, *board.coords(4, 0, centered=True))
        assert not board.violations()
        w = Location('W', '', -50, 0, 'country', 'iso2', 'iso3', 0, 0, Continent.AS)
        board.put(w, *board.coords(-4, 0, centered=True))
        assert not board.violations()
        n_e = Location('NE', '', 50, 50, 'country', 'iso2', 'iso3', 0, 0, Continent.NA)
        board.put(n_e, *board.coords(4, -4, centered=True))
        assert not board.violations()
        n_w = Location('NW', '', -50, 50, 'country', 'iso2', 'iso3', 0, 0, Continent.SA)
        board.put(n_w, *board.coords(-4, -4, centered=True))
        assert not board.violations()
        s_e = Location('SE', '', 50, -50, 'country', 'iso2', 'iso3', 0, 0, Continent.OC)
        board.put(s_e, *board.coords(4, 4, centered=True))
        assert not board.violations()
        s_w = Location('SW', '', -50, -50, 'country', 'iso2', 'iso3', 0, 0,
                       Continent.EU)
        old_placed = board.placed()
        vs = board.try_place(s_w, *board.coords(-4, 4, centered=True))
        assert not vs
        assert board.placed() == old_placed + 1

    def test_violations(self):
        center = Location('center', '', 0, 0, 'country', 'iso2', 'iso3', 0, 0,
                          Continent.EU)
        board = Board(center, Board.BoardOptions(10))
        loc = Location('L', '', -50, 0, 'country', 'iso2', 'iso3', 0, 0, Continent.EU)
        # right of center
        board.put(loc, *board.coords(2, 0, centered=True))
        vs = board.violations()
        assert len(vs) == 1 and vs[0].direction == Direction.LONGITUDE
        board.remove(*board.coords(2, 0, centered=True))
        # left of center
        loc = Location('L', '', 50, 0, 'country', 'iso2', 'iso3', 0, 0, Continent.AN)
        board.put(loc, *board.coords(-2, 0, centered=True))
        vs = board.violations()
        assert len(vs) == 1 and vs[0].direction == Direction.LONGITUDE
        board.remove(*board.coords(-2, 0, centered=True))
        # above of center
        loc = Location('L', '', 0, -50, 'country', 'iso2', 'iso3', 0, 0, Continent.AN)
        board.put(loc, *board.coords(0, -2, centered=True))
        vs = board.violations()
        assert len(vs) == 1 and vs[0].direction == Direction.LATITUDE
        board.remove(*board.coords(0, -2, centered=True))
        # below of center
        loc = Location('L', '', 0, 50, 'country', 'iso2', 'iso3', 0, 0, Continent.AF)
        old_placed = board.placed()
        vs = board.try_place(loc, *board.coords(0, 2, centered=True))
        assert len(vs) == 1 and vs[0] == Direction.LATITUDE
        assert board.placed() == old_placed

    def test_violations_regression_1(self):
        center = Location(city='Bangui', city_ascii='Bangui',
                          longitude=18.5628, latitude=4.3733,
                          country='Central African Republic',
                          country_iso2='CF', country_iso3='CAF',
                          population=889231, identifier=1140080881,
                          continent=Continent.AF, capital=True)
        board = Board(center, Board.BoardOptions(size=10,
                                                 tolerance=5.0,
                                                 wrap=False))
        assert not board.violations()
        andorra = Location(city='Andorra la Vella',
                           city_ascii='Andorra la Vella',
                           longitude=1.5, latitude=42.5,
                           country='Andorra', country_iso2='AD',
                           country_iso3='AND', population=22615,
                           identifier=1020828846,
                           continent=Continent.EU, capital=True)
        violations = board.try_place(andorra, x=3, y=4)
        assert len(violations) == 0
        madrid = Location(city='Madrid', city_ascii='Madrid',
                          longitude=-3.7033, latitude=40.4169, country='Spain',
                          country_iso2='ES', country_iso3='ESP', population=6211000,
                          identifier=1724616994, continent=Continent.EU, capital=True)
        violations = board.try_place(madrid, x=4, y=2)
        assert len(violations) == 1 and violations[0] == Direction.LONGITUDE
        violations = board.try_place(madrid, x=2, y=4)
        # latitude difference is within tolerance
        assert len(violations) == 0
        
        
        
