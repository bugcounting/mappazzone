"""This module provides classes for a game board, consisting of a grid of locations."""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging

from .locations import Direction, Location


@dataclass
class Invalid:
    """
    A witness of a violation of the board invariant.

    An instance of this class identifies two locations on the board that violate 
    the invariant along a given coordinate direction.

    Attributes:
        direction: The coordinate direction along which the invariant was violated.
        x_1: The x coordinate of the first location.
        y_1: The y coordinate of the first location.
        x_2: The x coordinate of the second location.
        y_2: The y coordinate of the second location.
        loc1: The first location.
        loc2: The second location.
    """

    direction: Direction
    x_1: int
    y_1: int
    x_2: int
    y_2: int
    loc1: Location
    loc2: Location

    def __bool__(self):
        return False


class Board:
    """
    The board of the game.

    The board is a grid of locations. The invariant is that each pair of locations of the board 
    is placed on the grid in a way that respects the order of the locations 
    along the longitude and latitude directions.

    Attributes:
        grid: The bidimensional grid of locations. 
              grid[x][y] is the location placed on row y and column x.
        opts: Options for the board: size, center, tolerance, and whether to wrap.
    """

    @dataclass
    class BoardOptions:
        """
        Options for the board.

        Attributes:
            size: The size of the square board (number of cells on each side).
            tolerance: The tolerance for checking the relative order of coordinates.
            wrap: Whether longitudes should wraps over.
            center_x: The x coordinate of the center of the board.
            center_y: The y coordinate of the center of the board.
        """
        size: int
        tolerance: float = 0.0
        wrap: bool = False
        center_x: int = -1
        center_y: int = -1

    grid: List
    opts: BoardOptions

    _logger: logging.Logger

    def __init__(self, center: Location, options: BoardOptions):
        """Initialize board with `center` location and `options`."""
        self.log_setup()
        tolerance = options.tolerance
        wrap = options.wrap
        base_size = options.size
        size_2 = base_size // 2
        size = 1 + 2 * size_2
        self.opts = Board.BoardOptions(size=size, center_x=size_2, center_y=size_2,
                                       tolerance=tolerance, wrap=wrap)
        self.grid = [[None for _ in range(self.opts.size)]
                     for _ in range(self.opts.size)]
        self.grid[self.opts.center_x][self.opts.center_y] = center
        self._logger.debug('Initialized board with size: %s', self.opts.size)

    def __str__(self) -> str:
        """Representation of the board as a list of the locations at each position."""
        result = [f'Grid {self.opts.size}x{self.opts.size}:']
        # pylint: disable=invalid-name  # x and y are valid names for coordinate variables.
        for x in range(self.opts.size):
            for y in range(self.opts.size):
                location = self.get(x, y)
                result += [f'x={x}, y={y}: {location}']
        return '\n'.join(result)

    def log_setup(self):
        """Set up logger for this class."""
        self._logger = logging.getLogger(__name__)

    def set_center(self, center: Location):
        """Set the center location of the board."""
        self.grid[self.opts.center_x][self.opts.center_y] = center

    def get_center(self) -> Location:
        """Return the center location of the board."""
        return self.grid[self.opts.center_x][self.opts.center_y]

    # pylint: disable=invalid-name  # x and y are valid names for coordinate variables.
    def coords(self, x: int, y: int, centered: bool = False) -> Tuple[int, int]:
        """Return pair of absolute coordinates `x`, `y`. If
        `centered`, `x` and `y` are interpreted as relative offsets
        from the center, and translated into absolute coordinates."""
        if centered:
            x = self.opts.center_x + x
            y = self.opts.center_y + y
        return (x, y)

    # pylint: disable=invalid-name  # x and y are valid names for coordinate variables.
    def get(self, x: int, y: int) -> Optional[Location]:
        """Return location at absolute coordinates `x`, `y`. Fail if
        `x` or `y` are out of bounds."""
        if not (0 <= x < self.opts.size and 0 <= y < self.opts.size):
            raise ValueError(f'Position: {x}, {y} is out of bounds')
        return self.grid[x][y]

    # pylint: disable=invalid-name  # x and y are valid names for coordinate variables.
    def put(self, location: Optional[Location], x: int, y: int, force=False):
        """Place `location` at absolute coordinates `x`, `y` without
        checking invariant.  Fail if `x` or `y` are out of bound, or
        if not `force` and the position is already occupied."""
        current = self.get(x=x, y=y)
        if not force:
            assert current is None, f'Position {x}, {y} is occupied'
        self.grid[x][y] = location

    def remove(self, x: int, y: int):
        """Remove location at absolute coordinates `x`, `y`."""
        self.put(None, x, y, force=True)

    def placed(self) -> int:
        """Number of locations placed on the board (including the center)."""
        return len([cell for row in self.grid for cell in row if cell is not None])

    # pylint: disable=too-many-locals  # The invariant involves many (quantified) variables.
    def violations(self, direction: Optional[Direction] = None) -> List[Invalid]:
        """
        Check the invariant and return [] if it holds. Otherwise,
        return a list of the first `Invalid` violations of the invariant.

        The invariant corresponds to the predicate:

        (forall 0 <= x1 <= x2 < size:
           forall 0 <= y1, y2 < size:
             (grid[x1][y1] != None and grid[x1][y1] != None
              ==>
              grid[x1][y1].longitude.before(grid[x2][y2]))
        and
        (forall 0 <= y1 <= y2 < size:
           forall 0 <= x1, x2 < size:
             (grid[x1][y1] != None and grid[x1][y1] != None
              ==> 
              grid[x1][y1].latitude.before(grid[x2][y2]))
        """
        if direction is None:
            val_lng = self.violations(Direction.LONGITUDE)
            val_lat = self.violations(Direction.LATITUDE)
            return val_lng + val_lat
        checked = set([])
        for m1 in range(self.opts.size):
            for m2 in range(m1, self.opts.size):
                for n1 in range(self.opts.size):
                    for n2 in range(self.opts.size):
                        if direction == Direction.LONGITUDE:
                            x1, y1, x2, y2 = m1, n1, m2, n2
                        elif direction == Direction.LATITUDE:
                            x1, y1, x2, y2 = n1, m1, n2, m2
                        check = (x1, y1, x2, y2)
                        if check in checked:
                            continue
                        checked.add(check)
                        first, second = self.grid[x1][y1], self.grid[x2][y2]
                        if first is None or second is None:
                            continue
                        if first.before(second, direction, self.opts.tolerance):
                            continue
                        return [Invalid(direction,
                                        x1, y1, x2, y2,
                                        first, second)]
        return []

    def try_place(self, location: Location, x: int, y: int) -> List[Direction]:
        """Try to place `location` at absolute coordinates `x`, `y` on
        the board. If doing so does not break the invariant, return
        []. Otherwise, removes `location` from the board and return a
        list of directions where the placement would have violated the
        invariant."""
        self._logger.debug('Try placement of %s at x=%s, y=%s', location, x, y)
        current = self.get(x=x, y=y)
        if current is not None:
            self._logger.debug('Position: x=%s, y=%s is occupied', x, y)
            raise ValueError(f'Position: {x}, {y} is occupied')
        self.put(location=location, x=x, y=y, force=False)
        self._logger.debug('Location placed at: x=%s, y=%s', x, y)
        check = self.violations()
        for violation in check:
            self._logger.debug('Found violation: %s', violation)
        if len(check) > 0:
            self._logger.debug(
                'Violations found: removing location from x=%s, y=%s', x, y)
            self.remove(x=x, y=y)
        return [v.direction for v in check]
