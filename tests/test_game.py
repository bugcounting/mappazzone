import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src/mappazzone')

from constants import ENV_LANGUAGE
os.environ[ENV_LANGUAGE] = 'EN'
from locations import Continent, Direction, Location, Locations
from options import Options
from game import Player, Game


class TestPlayer:

    def player(self) -> Player:
        loc1 = Location('C1', '', 10, 0, 'country', '', '', 0, 1, Continent.EU)
        loc2 = Location('C2', '', 20, 0, 'country', '', '', 0, 1, Continent.AS)
        p = Player('name')
        p.deal([loc1, loc2])
        return p

    def test_deal(self):
        p = self.player()
        assert p.score() == 2

    def test_play(self):
        p = self.player()
        loc = p.hand[0]
        p.play(loc)
        assert p.score() == 1
        with pytest.raises(ValueError) as ex:
            p.play(loc)

    def test_swap(self):
        p = self.player()
        loc = p.hand[0]
        old_score = p.score()
        loc3 = Location('C3', '', -20, -10, 'country', '', '', 0, 1, Continent.NA)
        p.swap(loc, loc3)
        assert p.score() == old_score
        assert loc not in p.hand
        assert loc3 in p.hand
        with pytest.raises(ValueError) as ex:
            p.swap(loc, loc3)


class TestGame:

    def game(self) -> Game:
        locations_list = [
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
        locations = Locations(content=locations_list)
        old_locations = len(locations)
        options = Options()
        options.set_option('capitals only', False)
        options.set_option('initial cities', 2)
        game =  Game(options=options,
                     players=['P1', 'P2'],
                     locations=locations)
        assert len(game.deck) == old_locations - (1 + 2 * 2)
        return game

    def test_init(self):
        game = self.game()
        assert game.board.violations() == []
        
    def test_swap(self):
        game = self.game()
        p1, p2 = game.players
        hand_p1, hand_p2 = len(p1.hand), len(p2.hand)
        game.swap(p1, p1.hand[0])
        assert len(p1.hand) == hand_p1
        game.swap(p2, p2.hand[0])
        assert len(p2.hand) == hand_p2
        # It is not p2's turn now
        with pytest.raises(ValueError) as ex:
            game.swap(p2, p2.hand[0])

    def test_place(self):
        game = self.game()
        p1, p2 = game.players
        hand_p1, hand_p2 = len(p1.hand), len(p2.hand)
        loc1 = p1.hand[0]
        center = Location('X', '', loc1.longitude - 10, loc1.latitude + 10,
                          'country', '', '', 0, 1, Continent.EU, False)
        assert center.before(loc1, direction=Direction.LONGITUDE, tolerance=0.0)
        assert center.before(loc1, direction=Direction.LATITUDE, tolerance=0.0)
        game.board.set_center(center)
        x, y = game.board.coords(1, 1, centered=True)
        result = game.place(p1, loc1, x, y)
        assert len(result) == 0
        # It is p2's turn now
        with pytest.raises(ValueError) as ex:
            game.place(p1, loc1, x, y)
        game = self.game()
        p1, p2 = game.players
        hand_p1, hand_p2 = len(p1.hand), len(p2.hand)
        loc1 = p1.hand[0]
        center = Location('X', '', loc1.longitude + 10, loc1.latitude - 10,
                          'country', '', '', 0, 1, Continent.EU, False)
        game.board.set_center(center)
        x, y = game.board.coords(1, 1, centered=True)
        old_score = p1.score()
        result = game.place(p1, loc1, x, y)
        assert len(result) == 2
        fact = len(result) if game.options['draw per mistake'] else 1
        assert p1.score() == old_score - 1 + game.options['draw when fail'] * fact

        

        
        
    
        

        
        
