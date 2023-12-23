import sys
import os
import time
import tkinter as tk
import pytest
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')

from mappazzone.constants import ENV_LANGUAGE
os.environ[ENV_LANGUAGE] = 'EN'
from mappazzone.mappazzone import run
from mappazzone.themes import Messages
from mappazzone.locations import Continent, Direction, Location
from mappazzone.ui import GameUI


class TestUI:

    # https://stackoverflow.com/a/49028688
    def pump_events(self, root: tk.Tk):
        """Process all pending events in `root`."""
        while root.dooneevent(tk._tkinter.ALL_EVENTS | tk._tkinter.DONT_WAIT):
            pass

    def find_button(self, top: tk.Frame, text: str) -> tk.Button:
        """Find button in `top` with given text."""
        for _name, widget in top.children.items():
            if isinstance(widget, tk.Button) and widget.cget('text') == text:
                return widget

    def pause(self):
        """Take a short pause, so that the user can visually inspect the UI state."""
        time.sleep(3)

    def test_ui(self):
        """This test runs a short game through the UI by manipulating
        its components and event loop. As the test runs, visually
        inspect the UI at each pause, to confirm that it runs as expected."""
        msg = Messages()
        app = run('EN', True, None, startloop=False)
        self.pump_events(app)
        main = app._frame
        # Set up only one city in hand
        app.options.set_option('initial cities', 1)
        # Fill in name for player
        player_entry = main.player_entries[0]
        player_entry.insert(0, 'Player')
        self.pause()
        # Start game
        main.start_game()
        # Force reassignment of center and player's hand
        rome = Location(city='Rome', city_ascii='Rome',
                        longitude=12.4828, latitude=41.8931,
                        country='Italy',
                        country_iso2='IT', country_iso3='ITA',
                        population=2872800, identifier=1380382862,
                        continent=Continent.EU, capital=True)
        reykjavik = Location(city='Reykjavík', city_ascii='Reykjavik',
                             longitude=-21.9400, latitude=64.1467,
                             country='Iceland',
                             country_iso2='IS', country_iso3='ISL',
                             population=135688, identifier=1352327190,
                             continent=Continent.EU, capital=True)
        app.game.board.set_center(rome)
        player = app.game.players[0]
        player.hand = [reykjavik]
        # Reload game with new center and hand
        app.switch_frame(GameUI)
        self.pump_events(app)
        self.pause()
        # Do an incorrect placement of reykjavik
        game = app._frame
        # Select the only location in hand
        game.set_selected(0)
        center_x, center_y = app.game.board.opts.center_x, app.game.board.opts.center_y
        # Place south east
        game.place_selected(x=center_x + 1, y=center_y + 1)
        self.pump_events(app)
        self.pause()
        # Mistakes were made
        assert len(player.hand) == app.options.to_draw([Direction.LONGITUDE, Direction.LATITUDE],
                                                       1)
        # Reload game showing new cities drawn
        app.switch_frame(GameUI)
        self.pump_events(app)
        self.pause()
        # Reset player hand
        player.hand = [reykjavik]
        # Reload game with reset hand
        app.switch_frame(GameUI)
        self.pump_events(app)
        self.pause()
        # Do an correct placement of reykjavik
        game = app._frame
        # Select the only location in hand
        game.set_selected(0)
        # Place north west
        game.place_selected(x=center_x - 1, y=center_y - 1)
        self.pump_events(app)
        self.pause()
        # Player placed everything
        assert len(player.hand) == 0
        # Reload game showing that player has won
        app.switch_frame(GameUI)
        self.pump_events(app)
        self.pause()
