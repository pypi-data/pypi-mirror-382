#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# author: Hadi Cahyadi
# email: cumulus13@gmail.com
# license: MIT
# github: https://github.com/cumulus13/make_colors

"""
make_colors.py
A module to provide colored text output.
"""

from __future__ import print_function

import os
import sys
import re

MODE = 0
_print = print

if sys.platform == 'win32':
    import ctypes
    kernel32 = ctypes.WinDLL('kernel32')
    hStdOut = kernel32.GetStdHandle(-11)
    mode = ctypes.c_ulong()
    MODE = mode
    if not mode.value == 7:
        kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
        mode.value |= 4
        kernel32.SetConsoleMode(hStdOut, mode)

class MakeColors(object):
    """A class that provides methods for generating colored text output in Windows 10 and above.

    Attributes:
        supports_color(classmethod): Class method to check if the system supports colored text output.
        colored(method): Method to generate colored text output.
    """
    
    def __init__(self):
        super(MakeColors, self).__init__()

    @classmethod
    def supports_color(cls):
        """Check if sys.stdout is a tty and if it supports colors.

        Args:
            cls(type): The class this method is attached to.

        Returns:
            bool: True if sys.stdout is a tty and supports colors, False otherwise.

        Raises:
            AttributeError: If sys.stdout does not have the isatty attribute.
        """
        plat = sys.platform
        supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)

        # isatty is not always implemented, #6223.  
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        
        global MODE
        if plat == 'win32' and int(MODE.value) == 7:
            supported_platform = True
        return supported_platform and is_a_tty
    
    def colored(self, string, foreground, background, attrs=[]):
        """Colorizes a given string using ANSI escape codes.

        Args:
            string(str): The string to colorize.
            foreground(str): Foreground color (e.g., 'red', 'green', 'blue').
            background(str): Background color (e.g., 'on_red', 'on_green', 'on_blue').
            attrs(list): List of attributes (e.g., ['bold', 'underline']).

        Returns:
            str: The colorized string.

        Raises:
            KeyError: If an invalid foreground or background color is specified.
        """
        
        # attrs_bank = {}
        # reset = ''
        # bold = ''
        # underline = ''
        # inverse = ''
        # if attrs:
        #     for i in attrs:
        #         if i == 'reset':
        #             reset = '0m'
        #         elif i == 'bold':
        #             bold = '1m'
        #         elif i == 'underline':
        #             underline = '4m'
        #         elif i == 'inverse':
        #             inverse = '7m'
        #print("foreground =", foreground)
        #print("background =", background)
        fore_color_bank = {
            'black': '30m',
            'red': '31m',
            'green': '32m',
            'yellow': '33m',
            'blue': '34m',
            'magenta': '35m',
            'cyan': '36m',
            'white': '37m',

            'lightblack': '90m',
            'lightgrey': '90m',
            'lightred': '91m',
            'lightgreen': '92m',
            'lightyellow': '93m',
            'lightblue': '94m',
            'lightmagenta': '95m',
            'lightcyan': '96m',
            'lightwhite': '97m',

        }

        back_color_bank = {
            'black': '40m',
            'red': '41m',
            'green': '42m',
            'yellow': '43m',
            'blue': '44m',
            'magenta': '45m',
            'cyan': '46m',
            'white': '47m',

            'on_black': '40m',
            'on_red': '41m',
            'on_green': '42m',
            'on_yellow': '43m',
            'on_blue': '44m',
            'on_magenta': '45m',
            'on_cyan': '46m',
            'on_white': '47m',

            'lightblack': '100m',
            'lightgrey': '100m',
            'lightred': '101m',
            'lightgreen': '102m',
            'lightyellow': '103m',
            'lightblue': '104m',
            'lightmagenta': '105m',
            'lightcyan': '106m',
            'lightwhite': '107m',

            'on_lightblack': '100m',
            'on_lightgrey': '100m',
            'on_lightred': '101m',
            'on_lightgreen': '102m',
            'on_lightyellow': '103m',
            'on_lightblue': '104m',
            'on_lightmagenta': '105m',
            'on_lightcyan': '106m',
            'on_lightwhite': '107m',

        }

        background = back_color_bank.get(background)
        foreground = fore_color_bank.get(foreground)
        if not background:
            background = '40m'
        if not foreground:
            foreground = '37m'

        return "[%s;%s%s[0m" % (background[:-1], foreground, string)
        # return "\033[%s;%s%s\033[0m" % (background[:-1], foreground, string)

class MakeColorsError(Exception):
    """Custom exception class for MakeColors errors."""
    def __init__(self, color):
        self.color = color
        super(MakeColorsError, self).__init__("there is no color for %s" % color)

class MakeColorsWarning(Warning):
    """Custom warning class for MakeColors warnings."""
    def __init__(self, color):
        self.color = color
        super(MakeColorsWarning, self).__init__("there is no color for %s" % color)

class MakeColor(MakeColors):
    """Alias for MakeColors class."""
    pass

def color_map(color):
    if color and len(color) < 3:
        if color == 'b' or color == 'bk':
            color = 'black'
        elif color == 'bl':
            color = 'blue'
        elif color == 'r' or color == 'rd' or color == 're':
            color = 'red'
        elif color == 'g' or color == 'gr' or color == 'ge':
            color = 'green'
        elif color == 'y' or color == 'ye' or color == 'yl':
            color = 'yellow'
        elif color == 'm' or color == 'mg' or color == 'ma':
            color = 'magenta'
        elif color == 'c' or color == 'cy' or color == 'cn':
            color = 'cyan'
        elif color == 'w' or color == 'wh' or color == 'wi' or color == 'wt':
            color = 'white'
        elif color == 'lb':
            color = 'lightblue'
        elif color == 'lr':
            color = 'lightred'
        elif color == 'lg':
            color = 'lightgreen'
        elif color == 'ly':
            color = 'lightyellow'
        elif color == 'lm':
            color = 'lightmagenta'
        elif color == 'lc':
            color = 'lightcyan'
        elif color == 'lw':
            color = 'lightwhite'
        else:
            color = 'lightwhite'
        
    return color

def getSort(data=None, foreground='', background=''):
    """Parses color codes and returns foreground and background colors.

    Args:
        data(str | None): String containing foreground and background color codes separated by "-" or "_". If None, uses default values.
        foreground(str): Foreground color code. If empty, uses default value.
        background(str): Background color code. If empty, uses default value.

    Returns:
        Tuple[str, str]: Tuple containing the foreground and background colors.

    Raises:
        ValueError: If an invalid color code is provided.
    """
    if data:
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: data =", data)
        if "-" in data or "_" in data:
            foreground, background = re.split("-|_", data)
            if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
                _print("getSort: foreground [1] =", foreground)
                _print("getSort: background [1] =", background)
        else:
            foreground = data
            background = background
            if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
                _print("getSort: foreground [2] =", foreground)
                _print("getSort: background [2] =", background)
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"getSort: foreground: {foreground}")
        _print(f"getSort: background: {background}")
    if foreground and len(foreground) > 2 and ("-" in foreground or "_" in foreground):
        _foreground, _background = re.split("-|_", foreground)
        foreground = _foreground or foreground
        background = _background or background
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: foreground [3] =", foreground)
            _print("getSort: background [3] =", background)
    elif background and len(background) > 2 and ("-" in background or "_" in background):
        _foreground, _background = re.split("-|_", background)
        foreground = _foreground or foreground
        background = _background or background
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: foreground [4] =", foreground)
            _print("getSort: background [4] =", background)
    else:
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: foreground [5] =", foreground)
            _print("getSort: background [5] =", background)
            
        foreground = foreground or 'white'
        background = background or None
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: foreground [6] =", foreground)
            _print("getSort: background [6] =", background)
        if foreground and len(foreground) > 2 and background and len(background) > 2:
            return foreground, background
          
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"getSort: foreground before: {foreground}")
        _print(f"getSort: background before: {background}")
        
    if foreground and len(foreground) < 3:
        foreground = color_map(foreground)
    if background and len(background) < 3:
        background = color_map(background)
    
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"getSort: returning foreground: {foreground}")
        _print(f"getSort: returning background: {background}")
    return foreground, background

def make_colors(string, foreground = 'white', background=None, attrs=[], force = False):
    """Apply color formatting to a given string if color support is enabled and conditions are met.

    Args:
        string(str): The string to be colorized.
        foreground(str): Foreground color code or name (e.g., "red", "green", "1;31").
        background(str): Background color code or name (e.g., "blue", "44"). Defaults to None.
        attrs(list): List of attributes (e.g., ["bold", "underline"]). Defaults to an empty list.
        force(bool): Force colorization, ignoring environment variables. Defaults to False.

    Returns:
        str: The colorized string or the original string if colorization is disabled or unsupported.

    Raises:
        ValueError: If an invalid color code or attribute is provided.
    """
    # if not MakeColors.supports_color() or os.getenv('MAKE_COLORS') == '0':
    #     return string

    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"FOREGROUND: {foreground}")
        _print(f"BACKGROUND: {background}")
        
    if "-" in foreground or "_" in foreground:
        foreground, background = getSort(foreground)
    elif (foreground and len(foreground) < 3) or (background and len(background) < 3):
        foreground, background = getSort(foreground=foreground, background=background)
    
    _coloring = MakeColors()
    
    if force or os.getenv('MAKE_COLORS_FORCE') == '1' or os.getenv('MAKE_COLORS_FORCE') == 'True':
        return _coloring.colored(string, foreground, background, attrs)
    else:
        if not _coloring.supports_color() or os.getenv('MAKE_COLORS') == '0':
            return string
        elif os.getenv('MAKE_COLORS') == '1':
            return _coloring.colored(string, foreground, background, attrs)
        else:
            return _coloring.colored(string, foreground, background, attrs)

def make_color(string, foreground = 'white', background=None, attrs=[], force = False):
    """Alias for make_colors function.

    Args:
        string(str): The string to be colorized.
        foreground(str): Foreground color code or name (e.g., "red", "green", "1;31").
        background(str): Background color code or name (e.g., "blue", "44"). Defaults to None.
        attrs(list): List of attributes (e.g., ["bold", "underline"]). Defaults to an empty list.
        force(bool): Force colorization, ignoring environment variables. Defaults to False.

    Returns:
        str: The colorized string or the original string if colorization is disabled or unsupported.

    Raises:
        ValueError: If an invalid color code or attribute is provided.
    """
    return make_colors(string, foreground, background, attrs, force)
        
def print(string, foreground = 'white', background=None, attrs=[], force = False):
    """Prints a formatted string to the console.

    Args:
        string(str): The string to be printed.
        foreground(str): Foreground color of the string. Defaults to white.
        background(str | None): Background color of the string. Defaults to None.
        attrs(list[str]): List of attributes to apply to the string (e.g., bold, italic). Defaults to an empty list.
        force(bool): Force printing even if colors are not supported. Defaults to False.

    Returns:
        None: Returns None.

    Raises:
        ValueError: If an invalid color or attribute is specified.
        TypeError: If input types are not as expected.
    """
    _print(make_colors(string, foreground, background, attrs, force))

if __name__ == '__main__':
    _print(MakeColors.supports_color())
    _print(make_colors("This is Red", 'lw', 'lr'))
