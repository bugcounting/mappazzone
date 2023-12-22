from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging

from .locations import Direction, Location

    
@dataclass
class Invalid:
    direction: Direction
    x1: int
    y1: int
    x2: int
    y2: int
    loc1: Location
    loc2: Location

    def __bool__(self):
        return False

        
class Board:
    grid: List

    logger: logging.Logger

    @dataclass
    class BoardOptions:
        size: int
        tolerance: float=0.0
        wrap: bool=False

    def __init__(self, center: Location, options: BoardOptions):
        self.log_setup()
        self.tolerance = options.tolerance
        self.wrap = options.wrap
        self.base_size = options.size
        self.size_2 = self.base_size // 2
        self.size = 1 + 2 * self.size_2
        self.center_x = self.size_2
        self.center_y = self.size_2
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.grid[self.center_x][self.center_y] = center
        self.logger.debug(f'Initialized board with size: {self.size}')

    def __str__(self) -> str:
        result = [f'Grid {self.size}x{self.size}:']
        for x in range(self.size):
            for y in range(self.size):
                location = self.get(x, y)
                result += [f'x={x}, y={y}: {location}']
        return '\n'.join(result)

    def log_setup(self):
        self.logger = logging.getLogger(__name__)

    def set_center(self, center: Location):
        self.grid[self.center_x][self.center_y] = center

    def get_center(self) -> Location:
        return self.grid[self.center_x][self.center_y]
        
    def coords(self, x: int, y: int, centered: bool=False) -> Tuple[int, int]:
        """Return pair of absolute coordinates `x`, `y`. If
        `centered`, `x` and `y` are interpreted as relative offsets
        from the center."""
        if centered:
            x = self.center_x + x
            y = self.center_y + y
        return (x, y)

    def get(self, x: int, y: int) -> Optional[Location]:
        """Return location at absolute coordinates `x`, `y`. Fail if
        `x` or `y` are out of bounds."""
        if not (0 <= x < self.size and 0 <= y < self.size):
            raise ValueError(f'Position: {x}, {y} is out of bounds')
        return self.grid[x][y]

    def put(self, location: Optional[Location],
            x: int, y: int, force=False):
        """Place `location` at absolute coordinates `x`, `y` without
        checking invariant.  Fail if `x` or `y` are out of bound, or
        if not `force` and the position is already occupied."""
        current = self.get(x=x, y=y)
        if not force:
            assert current == None, f'Position {x}, {y} is occupied'
        self.grid[x][y] = location

    def remove(self, x: int, y: int):
        """Remove location at absolute coordinates `x`, `y`."""
        self.put(None, x, y, force=True)

    def placed(self) -> int:
        """Number of locations placed on the board (including the center)."""
        return len([cell for row in self.grid for cell in row if cell is not None])

    def violations(self, direction: Optional[Direction]=None) -> List[Invalid]:
        """Check the invariant and return [] if it holds. Otherwise,
        return a list of the first `Invalid` violations of the invariant."""
        # (forall 0 <= x1 <= x2 < size:
        #  forall 0 <= y1, y2 < size:
        #  grid[x1][y1] != None and grid[x1][y1] != None
        #  ==> grid[x1][y1].longitude.before(grid[x2][y2])
        # and
        # (forall 0 <= y1 <= y2 < size:
        #  forall 0 <= x1, x2 < size:
        #  grid[x1][y1] != None and grid[x1][y1] != None
        #  ==> grid[x1][y1].latitude.before(grid[x2][y2])
        if direction == None:
            val_lng = self.violations(Direction.LONGITUDE)
            val_lat = self.violations(Direction.LATITUDE)
            return val_lng + val_lat
        checked = set([])
        for m1 in range(self.size):
            for m2 in range(m1, self.size):
                for n1 in range(self.size):
                    for n2 in range(self.size):
                        if direction == Direction.LONGITUDE:
                            x1, y1, x2, y2 = m1, n1, m2, n2
                        elif direction == Direction.LATITUDE:
                            x1, y1, x2, y2 = n1, m1, n2, m2
                        check = (x1, y1, x2, y2)
                        if check in checked:
                            continue
                        else:
                            checked.add(check)
                        first, second = self.grid[x1][y1], self.grid[x2][y2]
                        if first == None or second == None:
                            continue
                        if first.before(second, direction, self.tolerance):
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
        self.logger.debug(f'Try placement of {location} at x={x}, y={y}')
        current = self.get(x=x, y=y)
        if current is not None:
            self.logger.debug(f'Position: x={x}, y={y} is occupied')
            raise ValueError(f'Position: {x}, {y} is occupied')
        self.put(location=location, x=x, y=y, force=False)
        self.logger.debug(f'Location placed at: x={x}, y={y}')
        check = self.violations()
        for violation in check:
            self.logger.debug(f'Found violation: {violation}')
        if len(check) > 0:
            self.logger.debug(f'Violations found: removing location from x={x}, y={y}')
            self.remove(x=x, y=y)
        return [v.direction for v in check]
