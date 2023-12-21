from typing import List
import logging

from locations import Direction, Location, Locations
from board import Board
from options import Options


class Player:
    name: str
    hand: List[Location]
    placed: int

    logger: logging.Logger
    
    def __init__(self, name: str):
        self.log_setup()
        self.name = name
        self.hand = []
        self.placed = 0

    def log_setup(self):
        self.logger = logging.getLogger(__name__)

    def score(self) -> int:
        return len(self.hand)

    def placed_locations(self) -> int:
        return self.placed
    
    def deal(self, locations: List[Location]):
        self.logger.debug(f'Player {self.name} dealt locations: {locations}')
        self.hand += locations

    def play(self, location: Location):
        self.logger.debug(f'Player {self.name} playing location: {location}')
        if location not in self.hand:
            raise ValueError(f"Location {location} is not in {self.name}'s hand.")
        self.hand.remove(location)
        self.placed += 1

    def swap(self, loc_out: Location, loc_in: Location):
        self.logger.debug(f'Player {self.name} swapping: out {loc_out} in {loc_in}')
        if loc_out not in self.hand:
            raise ValueError(f"Location {loc_out} is not in {self.name}'s hand.")
        self.hand[self.hand.index(loc_out)] = loc_in


class Game:
    deck: Locations
    board: Board
    players: List[Player]
    rounds: int
    turn: int
    
    options: Options

    logger: logging.Logger

    def __init__(self, options: Options, players: List[str], locations: Locations):
        self.log_setup()
        if len(players) == 0:
            raise ValueError("Cannot play game without players.")
        self.logger.debug(f'Initializing game with players: {players}')
        self.options = options
        self.logger.debug(f'Initializing game with options: {options}')
        self.deck = locations
        self.deck.keep(capitals_only=self.options.capitals_only(),
                       continents=self.options.continents())
        self.logger.debug(f'Initializing game with {len(self.deck)} locations.')
        self.rounds = 0
        self.turn = 0
        # Pick center location
        center = self.deck.pick()[0]
        self.logger.debug(f'Center location: {center}')
        self.board = Board(center=center,
                           options=self.options.board())
        self.players = [Player(name) for name in players]
        # Pick initial hand of players
        for p in self.players:
            p.deal(self.deck.pick(self.options.initial()))

    def log_setup(self):
        self.logger = logging.getLogger(__name__)

    def current_player(self) -> Player:
        """The player who is playing next."""
        return self.players[self.turn]

    def swap(self, player: Player, location: Location):
        """The current player swaps one of the cards in their hand."""
        if player not in self.players or self.players.index(player) != self.turn:
            raise ValueError("Player {player} cannot play now")
        if not self.options.may_swap():
            raise ValueError("Swapping is now allowed")
        self.logger.debug(f'Player {player.name} swaps {location}')
        new_location = self.deck.pick()[0]
        player.swap(location, new_location)
        self.next_player()

    def place(self, player: Player,
              location: Location, x: int, y: int) -> List[Direction]:
        """The current player tries to place on the board one of the
        locations in their hand. Return list of offending directions,
        or the empty list if placement was successful."""
        if player not in self.players or self.players.index(player) != self.turn:
            raise ValueError("Player {player} cannot play now")
        self.logger.debug(f'Player {player.name} plays {location} at x={x}, y={y}')
        # Try to place it on board
        result = self.board.try_place(location, x, y)
        # Remove location from player's hand
        player.play(location)
        # If result was not successful, draw new locations
        player.deal(self.deck.pick(self.options.to_draw(result, player.score())))
        self.next_player()
        return result

    def next_player(self) -> bool:
        """Advance to next player, and return whether the game should continue."""
        self.turn = (self.turn + 1) % len(self.players)
        if self.turn == 0:
            self.rounds += 1
        return self.gameover()

    def gameover(self) -> str:
        """Is the game over?"""
        return self.options.gameover(rounds=self.rounds,
                                     scores=[p.score() for p in self.players],
                                     placed=self.board.placed(),
                                     deck=len(self.deck))

    def results(self) -> list[Player]:
        """List of players from top scorer (i.e., the one with the
        fewest cities in hand)."""
        players = sorted([(p, p.score(), p.placed_locations()) for p in self.players],
                         key=lambda e: (e[1], -e[2]))
        return [player for player, score, placed in players]

    

    






