from typing import Optional, List, Tuple
import logging
import copy
import platform
import os
# sudo apt-get install python3-tk idle3 python3-pil python3-pil.imagetk
# https://stackoverflow.com/a/49325719
import tkinter as tk
from tkinter import font as tkfont
from idlelib.tooltip import Hovertip
from PIL import Image, ImageTk
import textwrap

from constants import FLAGS_DIR
from utils import DisplayName, monitor_size
from themes import Messages
from options import Options
from locations import Direction, Location, Locations
from game import Game


class MappUI(tk.Tk):

    _frame: Optional[tk.Frame]
    options: Options
    locations: Locations
    player_names: List[str]
    game: Game

    messages: Messages
    logger: logging.Logger

    def __init__(self, options: Options, locations: Locations):
        tk.Tk.__init__(self)
        self.log_setup()
        self.messages = Messages()
        self.options = options
        self.locations = locations
        self.player_names = []
        self.title(self.messages['app name'])
        self._frame = None
        self.logger.debug(f'{self.__class__} initialized.')
        self.switch_frame(StartMenu)

    def log_setup(self):
        self.logger = logging.getLogger(__name__)

    def switch_frame(self, frame_class):
        """Destroy current frame and replace it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()
        self.logger.debug(f'Switching to frame {frame_class}.')


class StartMenu(tk.Frame):
    main: MappUI

    player_entries: List

    def __init__(self, main):
        tk.Frame.__init__(self, main)
        self.main = main
        self.player_entries = []
        self.build()
        self.main.logger.debug(f'{self.__class__} built.')

    def show_rules(self):
        rules_window = tk.Toplevel(self.main)
        rules_window.title(self.main.messages['app name']
                           + ': '
                           + self.main.messages['show rules'])
        rules_text = self.main.messages['how to play'].split('\n')
        rules_text = '\n'.join([line.strip() for line in rules_text])
        rules = tk.Label(rules_window, text=rules_text,
                         wraplength=0, anchor='w', justify=tk.LEFT)
        rules.pack()

    def add_player(self) -> int:
        """Add player entry. Return row index of first available row below players."""
        row = len(self.player_entries)
        ## If row is occupied, reposition the elements one row below
        for r in reversed(range(row, row + 2)):
            for w in self.grid_slaves(row=r):
                w.grid(row=r + 1)
        n = row + 1
        label = tk.Label(self, text=self.main.messages['player name'].format(n))
        label.grid(row=row, column=0, padx=5, pady=1, sticky='E')
        name = tk.Entry(self)
        name.grid(row=row, column=1, padx=5, pady=1, sticky='W')
        self.player_entries.append(name)
        self.main.logger.debug(f'Player entry created.')
        return row + 1

    def start_game(self):
        """Collect non-empty player names and start game."""
        player_names = [p.get().strip() for p in self.player_entries]
        player_names = [p for p in player_names if p]
        if len(player_names) == 0:
            self.main.logger.debug(f'No player names: game cannot start.')
            return
        self.main.player_names = player_names
        # Copy locations so that the current filtering options can be applied
        locations = copy.deepcopy(self.main.locations)
        self.main.game = Game(options=self.main.options,
                              players=self.main.player_names,
                              locations=locations)
        self.main.switch_frame(GameUI)

    def build(self):
        """Build list of player name slots, and main buttons."""
        for n in range(2):
            row = self.add_player()
        add_button = tk.Button(self, text=self.main.messages['add player'],
                               command=lambda: self.add_player())
        add_button.grid(row=row, column=0, columnspan=1,
                        pady=1, padx=5, sticky='E')
        start_button = tk.Button(self, text=self.main.messages['start game'],
                                 command=lambda: self.start_game())
        start_button.grid(row=row, column=1, columnspan=1, pady=20, padx=10)
        row += 1
        opt_button = tk.Button(self, text=self.main.messages['options'],
                               command=lambda: self.main.switch_frame(OptionsMenu))
        opt_button.grid(row=row, column=0, columnspan=1, pady=10, padx=10)
        rules_button = tk.Button(self, text=self.main.messages['show rules'],
                               command=lambda: self.show_rules())
        rules_button.grid(row=row, column=1, columnspan=1, pady=10, padx=10)


class OptionsMenu(tk.Frame):
    main: MappUI
    options: Options

    def __init__(self, main):
        tk.Frame.__init__(self, main)
        self.main = main
        self.options = main.options
        self.build()

    def build(self):
        """List options with checkbox for boolean options and pull down menu for other kinds of options."""
        row = -1
        for _, option in self.options.items():
            row += 1
            label = tk.Label(self, text=option.name)
            label.grid(row=row, column=0, padx=5, sticky='E')
            tip = Hovertip(label, textwrap.fill(option.description, 25))
            if type(option.value) is bool:
                option._var = tk.BooleanVar()
                option._var.set(option.value)
                choices = tk.Checkbutton(self, text='', variable=option._var,
                                         command=(lambda o=option:
                                                  o.set(o._var.get())))
            else:
                option._var = tk.StringVar()
                option._var.set(str(option.value))
                option._var.trace('w', lambda *args, o=option: o.set(o._var.get()))
                choices = tk.OptionMenu(self, option._var,
                                        *[str(o) for o in option.choices])
            choices.grid(row=row, column=1, sticky='W')
        row += 1
        back_button = tk.Button(self, text=self.main.messages['back to main'],
                                command=lambda: self.main.switch_frame(StartMenu))
        back_button.grid(row=row, column=0, columnspan=1, pady=20, padx=10)


class GameUI(tk.Frame):
    main: MappUI

    game: Game
    size: int

    board_frame: tk.Frame
    hand_frame: tk.Frame
    tile_len: int
    location_width: int
    location_height: int
    
    selected: Optional[int]
    location_frames: List[tk.Frame]

    def __init__(self, main):
        tk.Frame.__init__(self, main)
        self.main = main
        self.game = main.game
        self.size = self.game.board.size
        self.location_frames = []
        self.selected = None
        # Maximize window
        # if platform.system() == 'Windows':
        #     self.main.state('zoomed')
        # else:
        #     self.main.attributes('-zoomed', True)
        self.set_sizes()
        # Every time GameUI is reloaded it's a new turn.
        self.turn()

    def set_sizes(self) -> int:
        """Determine a suitable size, in pixels, of the board's tiles,
        so that the whole board fits in about half of the current monitor."""
        monitor_width, monitor_height = monitor_size(self.main)
        frac = 2
        while True:
            tile_len = int(1/frac * monitor_width / self.size)
            if tile_len * self.size < monitor_height + 10:
                self.tile_len = tile_len
                break
            frac += 0.1
        remaining_width = int(monitor_width - (20 + self.size * tile_len))
        self.remaining_width = remaining_width
        frac = 1.0
        while True:
            location_width = int(remaining_width * frac / 2)
            location_height = int(location_width * 5/9)
            if location_height * 7 < monitor_height - 20:
                self.location_width = location_width
                self.location_height = location_height
                break
            frac -= 0.01
        self.main.logger.debug(f'Screen geometry: W={monitor_width} x H={monitor_height} pixels')
        self.main.logger.debug(f'Tile size: {tile_len} pixels per tile, {self.size * tile_len} overall')
        self.main.logger.debug(f'Remaining width: {remaining_width} pixels')
        self.main.logger.debug(f'Location geometry: W={location_width} x H={location_height} pixels')

    def turn(self):
        """Check if the game is over or whether the current turn should be played."""
        self.main.logger.debug('Reload board.')
        self.main.logger.debug(str(self.game.board))
        self.draw_board()
        if self.game.gameover():
            self.main.logger.debug('Game over: show results.')
            self.draw_results()
        else:
            self.main.logger.debug('Next turn.')
            self.draw_player()

    def set_selected(self, selected: Optional[int]):
        """Set the index of the location, among those in the current
        player's hand, that has last been clicked."""
        if selected == self.selected:
            # Selecting the same location means unselecting it
            self.selected = None
            self.main.logger.debug('Location unselected.')
        else:
            self.selected = selected
            self.main.logger.debug(f'Location {self.selected} selected.')
        for k in range(len(self.location_frames)):
            location_frame = self.location_frames[k]
            if k == self.selected:
                # Highlight the selected location
                location_frame.config(highlightbackground='red')
            else:
                # Unhighlight all the other locations
                location_frame.config(highlightbackground='white')

    def place_selected(self, x: int, y: int):
        """Try to place the selected location on the board at
        coordinates `x`, `y`."""
        try:
            player = self.game.current_player()
            location = player.hand[self.selected]
            result = self.game.place(player, location, x, y)
        except IndexError:
            # `self.selected` is out of bounds
            self.main.logger.debug('Selected location {self.selected} is out of bounds: player {player.name} only has {len(player.hand)} locations in hand.')
            return
        except TypeError:
            # `self.selected` is None
            self.main.logger.debug('Selected location is None: cannot place.')
            return
        except ValueError:
            # The cell at `x`, `y` is occupied
            self.main.logger.debug(e)
            return
        if len(result) > 0:
            # Highlight wrong coordinates
            self.main.logger.debug('Highlight wrong coordinates: {result}.')
            placed_button = self.location_on_board(location,
                                                   highlight=result, highlightcol='red')
        else:
            # Highlight both coordinates as correct
            self.main.logger.debug('Highlight both coordinates as correct.')
            placed_button = self.location_on_board(location,
                                                   highlight=[Direction.LONGITUDE,
                                                              Direction.LATITUDE],
                                                   highlightcol='green')
        placed_button.grid(row=y, column=x)
        # Wait, and then reload GameUI
        self.after(self.game.options.turn_delay() * 1000,
                   lambda: self.main.switch_frame(GameUI))

    def swap_selected(self, selected: int):
        """Swap the selected location."""
        # Double click also selects the location.
        self.set_selected(selected)
        player = self.game.current_player()
        location = player.hand[selected]
        # Swap
        self.game.swap(player, location)
        # Reload GameUI
        self.main.switch_frame(GameUI)

    def draw_results(self):
        """Display the information about who won the game."""
        self.hand_frame = tk.Frame(self, pady=30)
        self.hand_frame.pack()
        gameover = self.main.game.gameover()
        gameover_label = tk.Label(self.hand_frame,
                                  text=textwrap.fill(gameover, 40),
                                  font=tkfont.Font(size=16))
        gameover_label.grid(row=0, column=0, columnspan=2, pady=20, padx=20)
        results = self.main.game.results()
        longest_name = sorted([p.name for p in results], key=len)[-1]
        name_label = DisplayName(longest_name, int(0.5 * self.remaining_width),
                                 padx=0, truncate=False)
        fontsize = min(24, name_label.fontsize())
        for n in range(len(results)):
            player = results[n]
            name = player.name
            n_label = tk.Label(self.hand_frame,
                               text=f'{n + 1}:',
                               font=tkfont.Font(size=fontsize))
            n_label.grid(row=n + 1, column=0, padx=5, sticky='E')
            name_label = tk.Label(self.hand_frame,
                                  text=name,
                                  font=tkfont.Font(size=fontsize))
            name_label.grid(row=n + 1, column=1, padx=5, sticky='W')
        back_button = tk.Button(self.hand_frame,
                                text=self.main.messages['back to main'],
                                command=lambda: self.main.switch_frame(StartMenu))
        back_button.grid(row=n + 2, column=0, pady=20, sticky='S')
        quit_button = tk.Button(self.hand_frame, text=self.main.messages['quit'],
                                command=lambda: self.main.destroy())
        quit_button.grid(row=n + 2, column=1, pady=20, sticky='S')
        
    def draw_player(self):
        """Display the information about the current player and their hand."""
        self.hand_frame = tk.Frame(self, pady=30)
        self.hand_frame.pack()
        player = self.game.current_player()
        to_play = DisplayName(self.main.messages['whose turn'].format(player.name),
                              self.remaining_width, truncate=False)
        player_label = tk.Label(self.hand_frame,
                                text=str(to_play),
                                font=tkfont.Font(size=min(35, to_play.fontsize())))
        player_label.grid(row=0, column=0, columnspan=2, pady=7)
        instructions = self.main.messages['place instructions']
        instructions += ('\n' + self.main.messages['swap instructions']) \
            if self.main.options.may_swap() else ''
        instructions = DisplayName(instructions,
                                   self.remaining_width, padx=0, truncate=False)
        instructions_label = tk.Label(self.hand_frame,
                                     text=str(instructions),
                                     font=tkfont.Font(size=instructions.fontsize()))
        instructions_label.grid(row=1, column=0, columnspan=2, pady=5)
        for k in range(len(player.hand)):
            location = player.hand[k]
            row, col = k // 2, k % 2
            location_frame = self.location_in_hand(location)
            location_frame.grid(row=2+row, column=col, pady=10, padx=10)
            location_frame.bind("<Button-1>", lambda e, k=k: self.set_selected(k))
            location_frame.bind("<Double-Button-1>",
                                lambda e, k=k: self.swap_selected(k))
            self.location_frames.append(location_frame)

    def draw_board(self):
        """Display the information about the current board."""
        self.board_frame = tk.Frame(self, padx=10)
        self.board_frame.pack(side='left', anchor='center')
        for x in range(self.size):
            for y in range(self.size):
                location_frame = self.location_on_board(self.game.board.get(x, y))
                location_frame.grid(row=y, column=x)
                location_frame.bind("<Button-1>",
                                    lambda e, x=x, y=y: self.place_selected(x, y))

    def location_on_board(self, location: Optional[Location],
                          highlight: List[Direction]=[],
                          highlightcol: str='red') -> tk.Button:
        """Build a button with information about `location` and add it
        to `self.board_frame` without placing it. For each direction
        in `highlight`, display the corresponding direction in color
        `highlightcol`."""
        ## Add blank image to button, so that width and height can
        ## be specified in pixels
        tile_len = self.tile_len
        blank = tk.PhotoImage(width=1, height=1)
        location_frame = tk.Button(self.board_frame,
                                   image=blank,
                                   compound='c',
                                   width=tile_len, height=tile_len)
        location_frame.grid_columnconfigure(0, weight=1, uniform='fred')
        location_frame.grid_columnconfigure(1, weight=1, uniform='fred')
        location_frame.grid_rowconfigure(0, weight=1, uniform='fred')
        location_frame.grid_rowconfigure(1, weight=1, uniform='fred')
        location_frame.grid_propagate(False)
        if location is not None:
            location_name = DisplayName(location.city, tile_len)
            location_label = tk.Label(location_frame, text=location_name,
                                      font=tkfont.Font(size=location_name.fontsize()))
            Hovertip(location_label, location_name.name)
            location_label.grid(row=0, column=0, columnspan=2)
            country_name = DisplayName(location.country, 3/4 * tile_len)
            country_label = tk.Label(location_frame, text=country_name,
                                     font=tkfont.Font(size=country_name.fontsize()))
            Hovertip(country_label, country_name.name)
            country_label.grid(row=1, column=0, columnspan=2)
            longitude = int(round(location.longitude))
            coord_fontsize = DisplayName('-00', 0.35 * tile_len).fontsize()
            longitude_label = tk.Label(location_frame, text=longitude,
                                       font=tkfont.Font(size=coord_fontsize))
            if Direction.LONGITUDE in highlight:
                longitude_label.config(fg=highlightcol)
            longitude_label.grid(row=2, column=0)
            if longitude > 0:
                direction = self.main.messages['direction east']
            elif longitude < 0:
                direction = self.main.messages['direction west']
            else:
                direction = self.main.messages['direction null']
            direction_fontsize = DisplayName('W', 1/5*tile_len).fontsize()
            longitude_direction = tk.Label(location_frame, text=direction,
                                           font=tkfont.Font(size=direction_fontsize))
            longitude_direction.grid(row=3, column=0, pady=0)
            latitude = int(round(location.latitude))
            latitude_label = tk.Label(location_frame, text=latitude,
                                      font=tkfont.Font(size=coord_fontsize))
            if Direction.LATITUDE in highlight:
                latitude_label.config(fg=highlightcol)
            latitude_label.grid(row=2, column=1, pady=0)
            if latitude > 0:
                direction = self.main.messages['direction north']
            elif latitude < 0:
                direction = self.main.messages['direction south']
            else:
                direction = self.main.messages['direction null']
            latitude_direction = tk.Label(location_frame, text=direction,
                                           font=tkfont.Font(size=direction_fontsize))
            latitude_direction.grid(row=3, column=1, pady=0)
        return location_frame

    def location_in_hand(self, location: Location) -> tk.Frame:
        """Build a frame with information about `location` and add it
        to `self.hand_frame` without placing it."""
        cell_width, cell_height = self.location_width, self.location_height
        location_frame = tk.Frame(self.hand_frame,
                                  highlightthickness=4,
                                  highlightbackground='white',
                                  width=cell_width, height=cell_height)
        location_frame.grid_columnconfigure(0, weight=1, uniform="fred")
        location_frame.grid_columnconfigure(1, weight=2, uniform="fred")
        location_frame.grid_rowconfigure(0, weight=3, uniform="fred")
        location_frame.grid_rowconfigure(1, weight=2, uniform="fred")
        location_frame.grid_rowconfigure(2, weight=2, uniform="fred")
        location_frame.grid_propagate(False)
        # Location name
        location_name = DisplayName(location.city, int(0.7 * cell_width))
        location_label = tk.Label(location_frame, text=location_name,
                                  font=tkfont.Font(size=location_name.fontsize()))
        Hovertip(location_label, location_name.name)
        location_label.grid(row=0, column=0, columnspan=2)
        # Flag and Country, Continent
        ## Flag canvas
        flag_w = int(0.2 * cell_width)
        flag_h = int(2/3 * flag_w)
        flag_image = self.get_flag_image(location.country_iso3, size=(flag_w, flag_h))
        flag_canvas = tk.Canvas(location_frame,
                                width=flag_w, height=flag_h, borderwidth=0)
        flag_canvas.create_image(flag_w // 2, flag_h // 2,
                                 image=flag_image)
        # Keep a reference to the image to prevent garbage-collection
        flag_canvas.flag = flag_image
        flag_canvas.grid(row=1, column=0, rowspan=2, padx=20)
        ## Country, Continent
        country_name = DisplayName(location.country, int(0.5 * cell_width))
        country_label = tk.Label(location_frame, text=country_name,
                                 font=tkfont.Font(size=country_name.fontsize()))
        Hovertip(country_label, country_name.name)
        country_label.grid(row=1, column=1, padx=20)
        continent_name = DisplayName(location.continent.value,
                                     int(0.4 * cell_width))
        continent_label = tk.Label(location_frame, text=continent_name,
                                   font=tkfont.Font(size=min(continent_name.fontsize(),
                                                             country_name.fontsize())))
        Hovertip(continent_label, continent_name.name)        
        continent_label.grid(row=2, column=1, padx=20)
        return location_frame

    def get_flag_image(self, iso3: str, size: Tuple[int, int]) -> ImageTk.PhotoImage:
        """Load flag image for country with code `iso3`, and resize it to `size`."""
        path = os.path.join(FLAGS_DIR, f'{iso3.upper()}.png')
        if not os.path.exists(path):
            self.main.logger.debug(f"Couldn't find a flag for country {iso3}.")
            return tk.PhotoImage(width=size[0], height=size[1])
        image = Image.open(path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
