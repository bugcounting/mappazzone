"""This module provides utility functions for UI formatting and image generation."""

from dataclasses import dataclass
from typing import Tuple
import sys
import os

import tkinter as tk
from tkinter import font as tkfont
from PIL import Image
import screeninfo

from .constants import FLAGS_DIR

BLANK_FLAG = '_blank_'


def export_flags(outdir: str):
    """Write out all images of flags in package `flagpy` to `outdir`."""
    # Avoid introducing dependencies for function that is not normally used.
    # pylint: disable=import-outside-toplevel
    import flagpy
    import country_converter as coco
    import re
    for country in flagpy.get_country_list():
        code = coco.convert(names=[country], to='ISO3')
        assert isinstance(code, str)
        if len(code) != 3:
            # try remove leading 'the'
            country2 = re.sub(r'^the\s+', '', country.lower())
            code = coco.convert(names=[country2], to='ISO3')
            if not isinstance(code, str) or len(code) != 3:
                print(f'Could not find code of {country}', file=sys.stderr)
                continue
        outfname = os.path.join(outdir, code + '.png')
        flag = flagpy.get_flag_img(country)
        flag.save(outfname)
    # Also create "blank" flag
    flag = Image.new('RGB', (300, 200), 'white')
    outfname = os.path.join(outdir, '_blank_' + '.png')
    flag.save(outfname)


def monitor_size(main: tk.Tk) -> Tuple[int, int]:
    """Width and height of current monitor. This has a consistent
    behavior with multiple monitors (whereas winfo_screenwidth()
    includes all desktop area or only the current monitor in Linux
    and Windows respectively."""
    cur_x, cur_y = main.winfo_x(), main.winfo_y()
    monitors = screeninfo.get_monitors()
    for monitor in monitors:
        if (monitor.x <= cur_x <= monitor.width + monitor.x
                and monitor.y <= cur_y <= monitor.height + monitor.y):
            return (monitor.width, monitor.height)
    return (main.winfo_screenwidth(), main.winfo_screenheight())


@dataclass
class DisplayName:
    """
    Constructs a truncated version of a string, and determines a suitable font size to display it.

    Attributes:
        name: The string to be displayed.
        max_width: The maximum width of the displayed string in pixels.
        padx: Padding in characters, which also has to git within the maximum width.
        truncate: Whether to truncate the string if it is too long.
        long: The maximum length of the string before truncation.
    """

    name: str
    max_width: int
    padx: int = 2
    truncate: bool = True
    long: int = 16

    def fontsize(self) -> int:
        """Font size that fits the (truncated) string within the maximum width."""
        fontsize = 0
        while True:
            fontsize += 1
            font = tkfont.Font(size=fontsize)
            # Width of string in pixels
            width = font.measure(self.padx * ' ' + str(self))
            # Height of string in pixels
            # height = font.measure('linespace')
            if width > self.max_width:
                return fontsize - 1

    def __str__(self) -> str:
        name = self.name
        if self.truncate and len(name) > self.long:
            name = name[:self.long] + '.'
        return name


if __name__ == '__main__':
    if not os.path.exists(FLAGS_DIR):
        os.makedirs(FLAGS_DIR)
    if len(os.listdir(FLAGS_DIR)) == 0:
        export_flags(FLAGS_DIR)
    else:
        print(f'Output directory {FLAGS_DIR} exists and is not empty. Doing nothing.',
              file=sys.stderr)
