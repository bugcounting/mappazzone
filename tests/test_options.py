import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src/mappazzone')

from constants import ENV_LANGUAGE
os.environ[ENV_LANGUAGE] = 'EN'
from locations import Direction, Continent
from options import Option, Options


class TestOption:

    def test_set(self):
        opt = Option(name='option', description='', choices=[1, 2, 3], value=1)
        opt.set(2)
        assert opt.value == 2
        opt.set('3')
        assert opt.value == 3
        with pytest.raises(ValueError) as ex:
            opt.set(7)
        with pytest.raises(ValueError) as ex:
            opt.set(False)
        with pytest.raises(ValueError) as ex:
            opt.set('7')


class TestOptions:

    def test_getitem(self):
        opts = Options()
        assert opts['grid size'] == 10
        assert opts[Continent.AS.name] == True
        with pytest.raises(KeyError) as ex:
            opts['####']

    def test_get_option(self):
        opts = Options()
        assert opts.get_option('grid size').value == 10
        assert opts.get_option(Continent.AS.name).value == True
        with pytest.raises(KeyError) as ex:
            opts.get_option('####')

    def test_set_option(self):
        opts = Options()
        opts.set_option('grid size', 8)
        assert opts['grid size'] == 8
        opts.set_option('grid size', '8')
        assert opts['grid size'] == 8

    def test_items(self):
        opts = Options()
        n = 0
        for option_name, option in opts.items():
            n += 1
        assert n == len(opts._OPTIONS)

    def test_to_draw(self):
        opts = Options()
        opts.set_option('draw when fail', 1)
        opts.set_option('draw per mistake', False)
        opts.set_option('stop drawing', 10)
        assert opts.to_draw([Direction.LONGITUDE, Direction.LATITUDE], 3) == 1
        opts.set_option('draw per mistake', True)
        assert opts.to_draw([Direction.LONGITUDE, Direction.LATITUDE], 3) == 2
        assert opts.to_draw([Direction.LONGITUDE, Direction.LATITUDE], 9) == 1
        opts.set_option('draw when fail', 2)
        assert opts.to_draw([Direction.LONGITUDE, Direction.LATITUDE], 2) == 4
        opts.set_option('draw per mistake', False)
        assert opts.to_draw([Direction.LONGITUDE, Direction.LATITUDE], 2) == 2
        assert opts.to_draw([Direction.LONGITUDE, Direction.LATITUDE], 10) == 0
