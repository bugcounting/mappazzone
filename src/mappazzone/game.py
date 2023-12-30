"""This module provides classes for players and games of Mappazzone!"""

from typing import List
import logging

from .locations import Direction, Location, Locations
from .board import Board
from .options import Options


class Player:
    """
    A player of the game.

    Attributes:
        name: The name of the player.
        hand: The locations in the player's hand.
        placed: The number of locations placed by the player on the board.
    """
    name: str
    hand: List[Location]
    placed: int

    _logger: logging.Logger

    def __init__(self, name: str):
        """Create a player with the given name."""
        self.log_setup()
        self.name = name
        self.hand = []
        self.placed = 0

    def log_setup(self):
        """Set up logger for this class."""
        self._logger = logging.getLogger(__name__)

    def score(self) -> int:
        """The score of the player, that is, the number of locations still in their hand."""
        return len(self.hand)

    def placed_locations(self) -> int:
        """The number of locations placed by the player on the board during the game."""
        return self.placed

    def deal(self, locations: List[Location]):
        """Add locations to the player's hand."""
        self._logger.debug('Player %s dealt locations: %s',
                           self.name, locations)
        self.hand += locations

    def play(self, location: Location):
        """The player plays one of the locations in their hand, 
        which is then removed from the player's hand."""
        self._logger.debug('Player %s playing location: %s',
                           self.name, location)
        if location not in self.hand:
            raise ValueError(
                f"Location {location} is not in %s's hand." % self.name)
        self.hand.remove(location)
        self.placed += 1

    def swap(self, loc_out: Location, loc_in: Location):
        """The player swaps location `loc_out` in their hand with new location `loc_in`."""
        self._logger.debug(
            'Player %s swapping: out %s in %s', self.name, loc_out, loc_in)
        if loc_out not in self.hand:
            raise ValueError(
                f"Location {loc_out} is not in {self.name}'s hand.")
        self.hand[self.hand.index(loc_out)] = loc_in


class Game:
    """
    The game state.

    Attributes:
        deck: The locations in the deck.
        board: The game board.
        players: The players.
        rounds: The number of rounds played.
        turn: The index of the player whose turn it is.
        options: The options for the game.
    """

    deck: Locations
    board: Board
    players: List[Player]
    rounds: int
    turn: int
    options: Options

    _logger: logging.Logger

    def __init__(self, options: Options, players: List[str], locations: Locations):
        self.log_setup()
        if len(players) == 0:
            raise ValueError("Cannot play game without players.")
        self._logger.debug('Initializing game with players: %s', players)
        self.options = options
        self._logger.debug('Initializing game with options: %s', options)
        self.deck = locations
        self.deck.keep(capitals_only=self.options.capitals_only(),
                       continents=self.options.continents())
        self._logger.debug(
            'Initializing game with %s locations.', len(self.deck))
        self.rounds = 0
        self.turn = 0
        while True:
            try:
                # Pick center location (using deck.pick() since board.pick() is not yet available)
                center = self.deck.pick()[0]
                self._logger.debug('Center location: %s', center)
                self.board = Board(center=center,
                                   options=self.options.board())
                self.players = [Player(name) for name in players]
                # Pick initial hand of players
                for player in self.players:
                    player.deal(self.pick(self.options.initial()))
            except ValueError:
                self._logger.debug('Game initialization failed: retrying.')
            break

    def log_setup(self):
        """Set up logger for this class."""
        self._logger = logging.getLogger(__name__)

    def pick(self, k=1) -> List[Location]:
        """Return a list with `k` random locations and remove them from the deck.
        If options.only_sat(), then only locations that are placeable are drawn."""
        to_draw = k
        result = []
        while to_draw > 0:
            try:
                locs = self.deck.pick(to_draw)
            except ValueError as e:
                if self.options.only_sat():
                    self._logger.debug(
                        'Out of placeable cities: forcing gameover.')
                else:
                    self._logger.critical(
                        'It seems `pick` has been called in a gameover state.')
                raise e
            assert len(locs) == to_draw
            if self.options.only_sat():
                placeable = [l for l in locs if self.board.can_place(l)]
            else:
                placeable = locs
            result += placeable
            to_draw -= len(placeable)
        if len(result) != k:
            self._logger.critical('Expected %d cities got %d.', k, len(result))
        return result

    def current_player(self) -> Player:
        """The player who is playing next."""
        return self.players[self.turn]

    def swap(self, player: Player, location: Location):
        """The current player swaps one of the cards in their hand."""
        if player not in self.players or self.players.index(player) != self.turn:
            raise ValueError("Player {player} cannot play now")
        if not self.options.may_swap():
            raise ValueError("Swapping is now allowed")
        self._logger.debug('Player %s swaps %s', player.name, location)
        try:
            new_location = self.pick()[0]
        except ValueError as e:
            if self.options.only_sat():
                self.next_player()
                return
            raise e
        player.swap(location, new_location)
        self.next_player()

    # pylint: disable=invalid-name  # x and y are valid names for coordinate variables.
    def place(self, player: Player,
              location: Location, x: int, y: int) -> List[Direction]:
        """The current player tries to place on the board one of the
        locations in their hand. Return list of offending directions,
        or the empty list if placement was successful."""
        if player not in self.players or self.players.index(player) != self.turn:
            raise ValueError(f'Player {player} cannot play now')
        self._logger.debug(
            'Player %s plays %s at x=%s, y=%s', player.name, location, x, y)
        # Try to place it on board
        result = self.board.try_place(location, x, y)
        # Remove location from player's hand
        player.play(location)
        # If result was not successful, draw new locations
        try:
            player.deal(
                self.pick(self.options.to_draw(result, player.score())))
        except ValueError as e:
            if self.options.only_sat():
                pass
            else:
                raise e
        self.next_player()
        return result

    def next_player(self) -> bool:
        """Advance to next player, and return whether the game should continue."""
        self.turn = (self.turn + 1) % len(self.players)
        if self.turn == 0:
            self.rounds += 1
        return self.gameover()

    def gameover(self) -> str:
        """Is the game over? Return the reason, or the empty string if the game is not over."""
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
