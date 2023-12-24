"""This module provides entry points to run the game."""

import sys
import os
import logging
import logging.handlers
import locale
from pathlib import Path
import argparse
import platformdirs
import tkinter as tk

from .constants import LANGUAGES, ENV_LANGUAGE, APP_NAME


def handle_exception(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions."""
    # Ignore keyboard interrupts, so that users can terminate with Ctrl-C as usual.
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.getLogger('').error("Uncaught exception",
                                exc_info=(exc_type, exc_value, exc_traceback))


def log_setup(nolog=False, logdir=None):
    """Set up logger for the whole application."""
    if logdir is None:
        log_dir = Path(platformdirs.user_log_dir(APP_NAME))
    else:
        log_dir = Path(logdir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = Path(log_dir, f'{APP_NAME}.log')
    if nolog:
        logging.disable()
    else:
        logging.basicConfig(level=logging.DEBUG)
    # Remove deafult handler, introduced by basicConfig, so that it
    # does not log to terminal but only to file as defined below.
    logging.getLogger('').handlers.clear()
    # Log handler that writes messages to rotating log files.
    handler = logging.handlers.RotatingFileHandler(log_file, backupCount=5)
    handler.setLevel(logging.DEBUG)
    # Create message formatter.
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(funcName)-25s %(lineno)d %(levelname)-8s MESSAGE: %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)
    logging.handlers.RotatingFileHandler.doRollover(handler)
    sys.excepthook = handle_exception


def run(language, nolog, logdir, startloop=True) -> tk.Tk:
    """
    Run the application and return it.

    Args:
        language: The language of the application.
        nolog: Whether to disable logging.
        logdir: The directory where log files are stored.
    """
    log_setup(nolog=nolog, logdir=logdir)
    if language is None:
        # Determine system language
        lang, _charset = locale.getlocale()
        language = 'IT' if lang and lang.startswith('it_') else 'EN'
        logging.getLogger('').debug(
            'Language set to %s based on locale %s', language, lang)
    os.environ[ENV_LANGUAGE] = language
    # pylint: disable=import-outside-toplevel
    # Importing these modules requires os.environ[ENV_LANGUAGE] to be set.
    from .options import Options
    from .locations import Locations
    from .ui import MappUI
    app = MappUI(options=Options(), locations=Locations(load=True))
    if startloop:
        app.mainloop()
    return app


def main_gui():
    """Application entry point, with CLI options."""
    parser = argparse.ArgumentParser(
        description="The Mappazzone geolocalization game."
    )
    parser.add_argument('--language', choices=LANGUAGES, default=None,
                        help='Set language (default: use system language).')
    parser.add_argument('--nolog', action='store_true',
                        help='Disable logging.')
    parser.add_argument('--logdir', default=None,
                        help='Set directory where log files are stored.')
    args = parser.parse_args()
    run(args.language, args.nolog, args.logdir)


if __name__ == "__main__":
    main_gui()
