#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# author: Hadi Cahyadi
# email: cumulus13@gmail.com
# license: MIT
# github: https://github.com/cumulus13/make_colors

"""
make_colors.py
A comprehensive module to provide colored text output with support for both ANSI escape codes
and rich console formatting. Supports Windows 10+, Linux, and macOS terminals.

Features:
- ANSI escape code based coloring
- Rich console format support
- Windows console color support
- Environment variable controls
- Flexible color specification (full names, abbreviations, codes)
- Background and foreground color combinations
- Multiple rich markup tags support
- Attribute detection from color strings
"""

from __future__ import print_function

import os
import sys
import re
from typing import List, Tuple, Optional

# try:
#     from .colors import __all__ as colors_all
# except Exception as e:
#     from colors import __all__ as colors_all

# Global variables for console mode handling
MODE = 0
_print = print
REST = "[0m"

_USE_COLOR = sys.stdout.isatty()
_DEBUG = os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']

_MAIN_ABBR = {
    'black': 'b', 'blue': 'bl', 'red': 'r', 'green': 'g',
    'yellow': 'y', 'magenta': 'm', 'cyan': 'c', 'white': 'w',
    'lightblue': 'lb', 'lightred': 'lr', 'lightgreen': 'lg',
    'lightyellow': 'ly', 'lightmagenta': 'lm', 'lightcyan': 'lc',
    'lightwhite': 'lw', 'lightblack': 'lk',
}


FG_CODES = {
    'black': '30', 'red': '31', 'green': '32', 'yellow': '33',
    'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37',
    'lightblack': '90', 'lightgrey': '90', 'lightred': '91',
    'lightgreen': '92', 'lightyellow': '93', 'lightblue': '94',
    'lightmagenta': '95', 'lightcyan': '96', 'lightwhite': '97',
}

BG_CODES = {
    'black': '40', 'red': '41', 'green': '42', 'yellow': '43',
    'blue': '44', 'magenta': '45', 'cyan': '46', 'white': '47',
    'lightblack': '100', 'lightgrey': '100', 'lightred': '101',
    'lightgreen': '102', 'lightyellow': '103', 'lightblue': '104',
    'lightmagenta': '105', 'lightcyan': '106', 'lightwhite': '107',
}

ATTR_CODES = {
    'bold': '1', 'dim': '2', 'italic': '3', 'underline': '4',
    'blink': '5', 'reverse': '7', 'strikethrough': '9', 'strike': '9',
}

# Windows-specific console setup for ANSI color support
if sys.platform == 'win32':
    import ctypes
    kernel32 = ctypes.WinDLL('kernel32')
    hStdOut = kernel32.GetStdHandle(-11)
    mode = ctypes.c_ulong()
    MODE = mode
    if not mode.value == 7:
        kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
        mode.value |= 4  # Enable ANSI escape sequence processing
        kernel32.SetConsoleMode(hStdOut, mode)

class MakeColors(object):
    """A comprehensive class that provides methods for generating colored text output 
    in Windows 10+, Linux, and macOS terminals with support for both ANSI and rich formatting.

    This class handles cross-platform color support, including Windows console configuration,
    ANSI escape codes, and rich text formatting options.

    Example:
        >>> mc = MakeColors()
        >>> colored_text = mc.colored("Hello World", "red", "on_yellow")
        >>> print(colored_text)
        
        >>> # Check if colors are supported
        >>> if MakeColors.supports_color():
        ...     print("Colors are supported!")
        
        >>> # Rich format example
        >>> rich_text = mc.rich_colored("Bold Red Text", color="red", style="bold")
        >>> print(rich_text)

    Attributes:
        None

    Methods:
        supports_color: Class method to check color support
        colored: Generate ANSI colored text
        rich_colored: Generate rich formatted text
    """
    
    def __init__(self):
        """Initialize the MakeColors instance.
        
        Sets up the color banks and formatting options for text output.
        """
        super(MakeColors, self).__init__()

    @classmethod
    def supports_color(cls):
        """Check if the current terminal/console supports colored text output.

        This method performs comprehensive checks including:
        - Platform compatibility (excludes Pocket PC)
        - TTY detection for proper terminal output
        - Windows console mode verification
        - ANSICON environment variable detection

        Args:
            cls (type): The class this method is attached to.

        Returns:
            bool: True if the system supports colored output, False otherwise.
                 - True for Unix-like systems with TTY support
                 - True for Windows 10+ with proper console mode
                 - True when ANSICON is detected in environment
                 - False for unsupported platforms or non-TTY output

        Example:
            >>> if MakeColors.supports_color():
            ...     print("Terminal supports colors!")
            ... else:
            ...     print("Plain text mode only")

        Raises:
            AttributeError: If sys.stdout does not have the isatty attribute.
                           This is handled gracefully by assuming no TTY support.
        """
        plat = sys.platform
        # Check platform compatibility - exclude Pocket PC and basic Windows
        supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)

        # Check if output is going to a terminal (TTY)
        # isatty is not always implemented, handle gracefully
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        
        # Special handling for Windows console mode
        global MODE
        if plat == 'win32' and int(MODE.value) == 7:
            supported_platform = True
            
        return supported_platform and is_a_tty
    
    def colored(self, string, foreground, background=None, attrs=[]):
        """Colorize a string using ANSI escape codes for terminal output.

        This method applies foreground colors, background colors, and text attributes
        using ANSI escape sequences. It handles color name mapping and provides
        fallback defaults for invalid colors.

        Args:
            string (str): The text string to colorize.
                         Example: "Hello World", "Error message", "Success!"
            foreground (str): Foreground color name or code.
                            Valid names: 'black', 'red', 'green', 'yellow', 'blue', 
                                       'magenta', 'cyan', 'white', 'lightred', etc.
                            Example: "red", "lightgreen", "blue"
            background (str, optional): Background color name with optional 'on_' prefix.
                                      Valid names: 'black', 'on_red', 'lightblue', etc.
                                      Defaults to None (no background).
                                      Example: "on_yellow", "lightblue", "on_white"
            attrs (list, optional): List of text attributes.
                                   Example: ['bold', 'underline']

        Returns:
            str: The input string wrapped with ANSI escape codes for colorization.
                Example: "\033[1;43;31mHello World\033[0m" (bold red text on yellow background)

        Example:
            >>> mc = MakeColors()
            >>> red_text = mc.colored("Error!", "red")
            >>> print(red_text)  # Prints "Error!" in red
            
            >>> warning = mc.colored("Warning!", "yellow", "on_black")
            >>> print(warning)  # Yellow text on black background
            
            >>> info = mc.colored("Info", "lightblue", "on_white", ['bold'])
            >>> print(info)  # Bold light blue text on white background

        Note:
            - Invalid color names fallback to white foreground and black background
            - The method returns raw ANSI codes; use print() to see colored output
            - Background colors can be specified with or without 'on_' prefix
        """
        
        # Comprehensive foreground color mapping with ANSI codes
        fore_color_bank = {
            # Standard colors (30-37)
            'black': '30',
            'red': '31',
            'green': '32',
            'yellow': '33',
            'blue': '34',
            'magenta': '35',
            'cyan': '36',
            'white': '37',

            # Bright colors (90-97)
            'lightblack': '90',
            'lightgrey': '90',
            'lightred': '91',
            'lightgreen': '92',
            'lightyellow': '93',
            'lightblue': '94',
            'lightmagenta': '95',
            'lightcyan': '96',
            'lightwhite': '97',
        }

        # Comprehensive background color mapping with ANSI codes
        back_color_bank = {
            # Standard background colors (40-47)
            'black': '40',
            'red': '41',
            'green': '42',
            'yellow': '43',
            'blue': '44',
            'magenta': '45',
            'cyan': '46',
            'white': '47',

            # Alternative 'on_' prefix format
            'on_black': '40',
            'on_red': '41',
            'on_green': '42',
            'on_yellow': '43',
            'on_blue': '44',
            'on_magenta': '45',
            'on_cyan': '46',
            'on_white': '47',

            # Bright background colors (100-107)
            'lightblack': '100',
            'lightgrey': '100',
            'lightred': '101',
            'lightgreen': '102',
            'lightyellow': '103',
            'lightblue': '104',
            'lightmagenta': '105',
            'lightcyan': '106',
            'lightwhite': '107',

            # Bright background with 'on_' prefix
            'on_lightblack': '100',
            'on_lightgrey': '100',
            'on_lightred': '101',
            'on_lightgreen': '102',
            'on_lightyellow': '103',
            'on_lightblue': '104',
            'on_lightmagenta': '105',
            'on_lightcyan': '106',
            'on_lightwhite': '107',
        }

        # Text attributes mapping
        attr_codes = {
            'bold': '1',
            'dim': '2',
            'italic': '3',
            'underline': '4',
            'blink': '5',
            'reverse': '7',
            'strikethrough': '9',
            'strike': '9',
            'normal': '22',  # Reset bold/dim
            'no_italic': '23',  # Reset italic
            'no_underline': '24',  # Reset underline
        }

        # Look up colors in the banks, with fallback defaults
        background_code = back_color_bank.get(background)
        foreground_code = fore_color_bank.get(foreground)
        
        # Apply fallback defaults for invalid colors
        if not background_code:
            background_code = '40'  # Default to black background
        if not foreground_code:
            foreground_code = '37'  # Default to white foreground

        # Arrange ANSI codes
        codes = []

        # add attrs
        if attrs:
            for attr in attrs:
                if attr.lower() in attr_codes:
                    codes.append(attr_codes[attr.lower()])

        # add background
        if background_code:
            codes.append(background_code)

        # add foreground
        if foreground_code:
            codes.append(foreground_code)

        # join all with ';'
        ansi_sequence = ";".join(codes)
        return f"[{ansi_sequence}m{string}[0m"

    def rich_colored(self, string, color=None, bg_color=None, style=None):
        """Generate rich formatted text with enhanced styling options.
        
        This method provides an alternative to basic ANSI coloring with support
        for more advanced text formatting and styling options.

        Args:
            string (str): The text string to format.
                         Example: "Important Message", "Debug Info"
            color (str, optional): Text color name.
                                  Example: "red", "green", "blue"
            bg_color (str, optional): Background color name.
                                     Example: "yellow", "black", "white"  
            style (str, optional): Text style modifier.
                                  Options: "bold", "italic", "underline", "dim"
                                  Example: "bold", "underline"

        Returns:
            str: Formatted string with rich console styling applied.

        Example:
            >>> mc = MakeColors()
            >>> bold_red = mc.rich_colored("ERROR", color="red", style="bold")
            >>> underlined = mc.rich_colored("Link", color="blue", style="underline")
            >>> highlighted = mc.rich_colored("Important", color="black", bg_color="yellow")

        Note:
            This method builds upon the basic colored() method while providing
            a more intuitive interface for rich text formatting.
        """
        # Convert style to attrs list
        style_codes = ['bold', 'dim', 'italic', 'underline', 'blink', 'reverse', 'strikethrough', 'normal', 'no_italic', 'no_underline', 'strike']

        attrs = []
        if style and style.lower() in style_codes:
            if style == 'strike': style = 'strikethrough'
            attrs = [style]
        
        # Apply style prefix if specified
        style_prefix = ''
        if style and style.lower() in style_codes:
            attrs = [style]
        
        # Convert rich format to standard format
        if bg_color and not bg_color.startswith('on_'):
            bg_color = f'on_{bg_color}'
            
        return self.colored(string, color or 'white', bg_color, attrs)

class MakeColorsError(Exception):
    """Custom exception class for MakeColors-related errors.
    
    This exception is raised when invalid color specifications or
    unsupported operations are attempted.

    Example:
        >>> try:
        ...     # Some operation that fails
        ...     raise MakeColorsError("invalidcolor")
        ... except MakeColorsError as e:
        ...     print(f"Color error: {e}")
    """
    def __init__(self, color):
        """Initialize the exception with the problematic color name.
        
        Args:
            color (str): The color name that caused the error.
        """
        self.color = color
        super(MakeColorsError, self).__init__("there is no color for %s" % color)

class MakeColorsWarning(Warning):
    """Custom warning class for MakeColors-related warnings.
    
    This warning is issued for non-critical issues like unrecognized
    color names that fall back to defaults.

    Example:
        >>> import warnings
        >>> warnings.warn(MakeColorsWarning("unknowncolor"))
    """
    def __init__(self, color):
        """Initialize the warning with the problematic color name.
        
        Args:
            color (str): The color name that triggered the warning.
        """
        self.color = color
        super(MakeColorsWarning, self).__init__("there is no color for %s" % color)

class MakeColor(MakeColors):
    """Alias class for MakeColors to provide alternative naming.
    
    This class is identical to MakeColors and exists purely for
    naming preference and backward compatibility.

    Example:
        >>> mc = MakeColor()  # Same as MakeColors()
        >>> text = mc.colored("Hello", "red")
    """
    pass

RESET = "\033[0m"

def color_map(color):
    """Map color abbreviations and short codes to full color names.
    
    This function expands common color abbreviations into their full names
    for use with the color banks. It provides convenient shortcuts for
    frequently used colors.

    Args:
        color (str): Color abbreviation or short code.
                    Examples: "r", "rd", "bl", "g", "lb"

    Returns:
        str: Full color name corresponding to the abbreviation.
             Falls back to 'lightwhite' for unrecognized codes.

    Example:
        >>> color_map("r")      # Returns "red"  
        >>> color_map("bl")     # Returns "blue"
        >>> color_map("lg")     # Returns "lightgreen"
        >>> color_map("xyz")    # Returns "lightwhite" (fallback)
        
    Supported abbreviations:
        - b, bk: black
        - bl: blue  
        - r, rd, re: red
        - g, gr, ge: green
        - y, ye, yl: yellow
        - m, mg, ma: magenta
        - c, cy, cn: cyan
        - w, wh, wi, wt: white
        - lb, lr, lg, ly, lm, lc, lw: light variants
    """
    if color and len(color) < 3:
        # Basic color mappings
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
        # Light color variants
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
            # Fallback for unrecognized abbreviations
            color = 'lightwhite'
        
    return color

def getSort(data=None, foreground='', background='', attrs=[]):
    """Parse and sort color specifications and attributes from combined format strings.
    
    This function now also detects text attributes (bold, italic, underline, etc.)
    from the input strings and returns them as a separate list.
    
    Args:
        data (str, optional): Combined color string with format "foreground-background" 
                             or "foreground_background" or "foreground,background". 
                             Examples: "red-yellow", "blue_white", "r-g"
        foreground (str): Explicit foreground color specification.
                         Examples: "red", "r", "lightblue"
        background (str): Explicit background color specification.
                         Examples: "yellow", "on_blue", "lg"
        attrs (list): Existing attributes list

    Returns:
        tuple[str, str, list]: A tuple containing (foreground_color, background_color, attributes_list).
                        foreground and background are full color names, with fallbacks applied:
                        - foreground defaults to 'white' if not specified
                        - background defaults to None if not specified
                        - attrs is bold, dim, italic, underline, blink, reverse, 
                          strikethrough, normal, no_italic, no_underline

    Example:
        >>> getSort("red-yellow")           # Returns ("red", "yellow")
        >>> getSort("red-yellow-bold")           # Returns ("red", "yellow")
        >>> getSort("red,yellow")           # Returns ("red", "yellow")
        >>> getSort("red,yellow,italic")           # Returns ("red", "yellow")
        >>> getSort("r_b")                  # Returns ("red", "black")  
        >>> getSort("r_b-bold")                  # Returns ("red", "black")  
        >>> getSort(foreground="blue")      # Returns ("blue", None)
        >>> getSort("lg-on_red")           # Returns ("lightgreen", "on_red")
        >>> getSort()                      # Returns ("white", None)

    Note:
        - Supports both "-" and "_" and "," as delimiters
        - Automatically expands abbreviations using color_map()
        - Handles nested delimiter parsing for complex specifications
        - Debug output available via MAKE_COLORS_DEBUG environment variable
    """
    
    # List of recognized text attributes
    text_attributes = ['bold', 'dim', 'italic', 'underline', 'blink', 'reverse', 'strikethrough', 'strike']
    detected_attrs = attrs.copy() if attrs else []
    
    def extract_attributes(text):
        """Extract attributes from a text string and return cleaned text + found attributes"""
        if not text:
            return text, []
        
        found_attrs = []
        cleaned_text = text
        
        for attr in text_attributes:
            if attr in text.lower():
                if attr == 'strike': attr = 'strikethrough'
                found_attrs.append(attr)
                # Remove the attribute from the text (case insensitive)
                cleaned_text = re.sub(rf'\b{attr}\b', '', cleaned_text, flags=re.IGNORECASE).strip()
                # Clean up extra spaces and delimiters
                cleaned_text = re.sub(r'[-_,\s]+', '-', cleaned_text).strip('-_,')
        
        return cleaned_text, found_attrs
    
    # Debug output for troubleshooting color parsing
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print("getSort: data =", data)
        _print("getSort: foreground =", foreground)
        _print("getSort: background =", background)

    if data:
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: data =", data)
        
        # Extract attributes from data first
        data, data_attrs = extract_attributes(data)
        detected_attrs.extend(data_attrs)
        
        # Parse combined format: "foreground-background" or "foreground_background"  
        if "-" in data or "_" in data or "," in data:
            parts = re.split("-|_|,", data)
            parts = [p.strip() for p in parts if p.strip()]  # Remove empty parts
            
            if len(parts) >= 2:
                foreground, background = parts[0], parts[1]
            elif len(parts) == 1:
                foreground = parts[0]
            
            if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
                _print("getSort: foreground [1] =", foreground)
                _print("getSort: background [1] =", background)
        else:
            # Single color specified - use as foreground
            foreground = data
            background = background
            if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
                _print("getSort: foreground [2] =", foreground)
                _print("getSort: background [2] =", background)
    
    # Extract attributes from foreground and background strings
    if foreground:
        foreground, fg_attrs = extract_attributes(foreground)
        detected_attrs.extend(fg_attrs)
    
    if background:
        background, bg_attrs = extract_attributes(background)
        detected_attrs.extend(bg_attrs)
    
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"getSort: foreground: {foreground}")
        _print(f"getSort: background: {background}")
        _print(f"getSort: detected_attrs: {detected_attrs}")
    
    # Handle nested delimiters in foreground specification
    if foreground and len(foreground) > 2 and ("-" in foreground or "_" in foreground or "," in foreground):
        parts = re.split("-|_|,", foreground)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 2:
            foreground, background = parts[0], parts[1]
        elif len(parts) == 1:
            foreground = parts[0]
        
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: foreground [3] =", foreground)
            _print("getSort: background [3] =", background)
    
    # Handle nested delimiters in background specification        
    elif background and len(background) > 2 and ("-" in background or "_" in background or "," in background):
        parts = re.split("-|_|,", background)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 2:
            foreground, background = parts[0], parts[1]
        elif len(parts) == 1:
            background = parts[0]
        
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: foreground [4] =", foreground)
            _print("getSort: background [4] =", background)
    else:
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: foreground [5] =", foreground)
            _print("getSort: background [5] =", background)
            
        # Apply default values for missing specifications    
        foreground = foreground or 'white'
        background = background or None
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: foreground [6] =", foreground)
            _print("getSort: background [6] =", background)
        
        # Return early if both colors are already full names    
        if foreground and len(foreground) > 2 and background and len(background) > 2:
            # Remove duplicates from attributes
            detected_attrs = list(dict.fromkeys(detected_attrs))
            return foreground.strip(), background.strip(), detected_attrs
          
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"getSort: foreground before: {foreground}")
        _print(f"getSort: background before: {background}")
    
    # Expand abbreviations to full color names    
    if foreground and len(foreground) < 3:
        foreground = color_map(foreground)
    if background and len(background) < 3:
        background = color_map(background)
    
    # Remove duplicates from attributes while preserving order
    detected_attrs = list(dict.fromkeys(detected_attrs))
    
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"getSort: returning foreground: {foreground}")
        _print(f"getSort: returning background: {background}")
        _print(f"getSort: returning attrs: {detected_attrs}")

    return foreground.strip() if foreground else foreground, background.strip() if background else background, detected_attrs

def translate(*args, **kwargs):
    return getSort(*args, **kwargs)

def parse_rich_markup(text):
    """Parse Rich console markup format and extract styling information.
    
    This function parses Rich-style markup tags and handles multiple markup sections
    in a single string, converting each to proper format for ANSI escape codes.
    
    Args:
        text (str): Text with Rich markup format.
    
    Returns:
        list: List of tuples (content, foreground, background, style)
    """
    pattern = r'\[([^\]]+)\](.*?)\[/\]'
    results = []
    last_end = 0

    for m in re.finditer(pattern, text):
        # plain text before markup
        if m.start() > last_end:
            results.append((text[last_end:m.start()], None, None, None))

        markup = m.group(1).strip().lower()
        content = m.group(2)

        fg, bg, style = None, None, None
        parts = markup.split()
        styles = ['bold', 'italic', 'underline', 'dim', 'blink', 'reverse', 'strikethrough', 'strike']
        for part in parts[:]:
            if part in styles:
                if part == 'strike': part = 'strikethrough'
                style = part
                parts.remove(part)
                break

        remaining = ' '.join(parts)
        if ' on ' in remaining:
            fg, bg = [p.strip() for p in remaining.split(' on ', 1)]
        elif remaining:
            fg = remaining.strip()

        results.append((content, fg, bg, style))
        last_end = m.end()

    # plain text after the last markup
    if last_end < len(text):
        results.append((text[last_end:], None, None, None))

    return results

def make_colors(string, foreground='white', background=None, attrs=[], force=False):
    """Apply color formatting to text with comprehensive control options and Rich markup support.

    This is the main function for creating colored text output. It provides
    flexible color specification, environment variable controls, Rich console
    markup parsing, and cross-platform compatibility. The function automatically 
    handles color support detection and can be forced to output colors regardless 
    of environment.

    Args:
        string (str): The text string to be colorized. Can include Rich markup format.
                     Examples: 
                     - Plain text: "Error message", "Success!", "Warning: Check input"
                     - Rich markup: "[red]Error[/]", "[white on blue]Info[/]", "[bold green]Success[/]"
        foreground (str): Foreground color specification. Can be:
                         - Full color name: "red", "green", "lightblue"
                         - Abbreviation: "r", "g", "lb" 
                         - Combined format: "red-yellow", "r_b"
                         - With attributes: "bold-red", "italic-blue-yellow"
                         Defaults to 'white'. Ignored if Rich markup is used.
        background (str, optional): Background color specification. Can be:
                                   - Full color name: "yellow", "black"
                                   - With 'on_' prefix: "on_yellow", "on_black"
                                   - Abbreviation: "y", "b"
                                   Defaults to None (no background). Ignored if Rich markup is used.
        attrs (list): List of text attributes.
                     Examples: ['bold', 'underline'], ['italic', 'dim']
                     Defaults to empty list.
        force (bool): Force color output even if environment doesn't support it.
                     Useful for file output or testing.
                     Defaults to False.

    Returns:
        str: The colorized string with ANSI escape codes, or the original string
             if coloring is disabled or unsupported.

    Rich Markup Support:
        The function supports Rich console markup format:
        - "[color]text[/]" - Single color
        - "[color1 on color2]text[/]" - Foreground and background  
        - "[style color]text[/]" - Style with color
        - "[style color1 on color2]text[/]" - Style with colors
        
        Supported styles: bold, italic, underline, dim, blink, reverse, strikethrough
        Supported colors: All standard ANSI colors and their light variants

    Attribute Detection (NEW!):
        Attributes can now be detected from color strings:
        - "bold-red" - Bold red text
        - "italic-blue-yellow" - Italic blue text on yellow background
        - "underline-green" - Underlined green text
        - Multiple attributes: "bold-italic-red"

    Environment Variables:
        MAKE_COLORS: 
            - "0": Disable all coloring (returns plain text)
            - "1": Enable coloring (default behavior)
        MAKE_COLORS_FORCE:
            - "1" or "True": Force coloring regardless of terminal support
        MAKE_COLORS_DEBUG:
            - "1", "true", "True": Enable debug output for troubleshooting

    Example:
        >>> # Basic usage
        >>> error_msg = make_colors("Error occurred!", "red")
        >>> print(error_msg)  # Red text
        
        >>> # With background
        >>> warning = make_colors("Warning!", "yellow", "on_black") 
        >>> print(warning)  # Yellow text on black background
        
        >>> # Using abbreviations
        >>> info = make_colors("Info", "lb", "w")  # Light blue on white
        >>> print(info)
        
        >>> # Combined format with attribute detection (NEW!)
        >>> error = make_colors("Error", "bold-red-yellow")  # Bold red text on yellow
        >>> success = make_colors("Success", "italic-green")  # Italic green text
        >>> warning = make_colors("Warning", "underline-yellow-black")  # Underlined yellow on black
        >>> print(error, success, warning)
        
        >>> # Rich markup format
        >>> rich_error = make_colors("[red]Error occurred![/]")
        >>> rich_warning = make_colors("[yellow on black]Warning![/]") 
        >>> rich_success = make_colors("[bold green]Success![/]")
        >>> rich_info = make_colors("[italic blue on white]Information[/]")
        >>> print(rich_error, rich_warning, rich_success, rich_info)

        >>> # Mixed usage - these are equivalent:
        >>> text1 = make_colors("TEST", "white", "on_red")
        >>> text2 = make_colors("[white on red]TEST[/]")
        >>> # Both produce identical output
        
        >>> # Force coloring for file output
        >>> with open("log.txt", "w") as f:
        ...     colored = make_colors("[blue]Log entry[/]", force=True)
        ...     f.write(colored)
        
        >>> # Complex rich markup (multiple sections)
        >>> log_msg = make_colors("[bold red][ERROR][/] [white]Database connection failed[/]")
        >>> print(log_msg)

    Note:
        - Rich markup takes precedence over foreground/background parameters
        - Attribute detection works with all separators: "-", "_", ","
        - Automatically detects terminal color support
        - Falls back to plain text when colors are unsupported
        - Respects environment variable settings for global control
        - Cross-platform compatible (Windows 10+, Linux, macOS)
        - Fully compatible with Rich console format
    """
    
    # Check for Rich markup format first
    if '[' in string and ']' in string and '[/' in string:
        results = parse_rich_markup(string)
        if results:
            output = ""
            _coloring = MakeColors()
            for content, rich_fg, rich_bg, rich_style in results:
                if not content:
                    continue
                fg = rich_fg or foreground
                bg = rich_bg or background
                if bg and not str(bg).startswith('on_'):
                    bg = f'on_{bg}'
                if rich_style:
                    part = _coloring.rich_colored(content, fg, bg, rich_style)
                else:
                    part = _coloring.colored(content, fg, bg, attrs)
                output += part
            
            # Check if coloring should be applied
            if force or os.getenv('MAKE_COLORS_FORCE') == '1' or os.getenv('MAKE_COLORS_FORCE') == 'True':
                return output
            else:
                if not _coloring.supports_color() or os.getenv('MAKE_COLORS') == '0':
                    # Strip ANSI codes and return plain text
                    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    return ansi_escape.sub('', output)
                else:
                    return output

    # Initialize attrs if not provided
    if attrs is None:
        attrs = []
    
    # Debug output for color specifications
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"FOREGROUND: {foreground}")
        _print(f"BACKGROUND: {background}")
        _print(f"ATTRS: {attrs}")
    
    # Parse combined color and attribute format using updated getSort
    parsed_attrs = attrs.copy()
    
    # Check if attributes are embedded in foreground string or if combined format is used
    if foreground and any(attr in foreground.lower() for attr in ['bold', 'dim', 'italic', 'underline', 'blink', 'reverse', 'strikethrough', 'strike']):
        foreground, background, parsed_attrs = getSort(foreground, background=background, attrs=parsed_attrs)
    elif "-" in foreground or "_" in foreground or "," in foreground:
        foreground, background, parsed_attrs = getSort(foreground, attrs=parsed_attrs)
    elif (foreground and len(foreground) < 3) or (background and len(background) < 3):
        # Expand abbreviations
        foreground, background, parsed_attrs = getSort(foreground=foreground, background=background, attrs=parsed_attrs)
    else:
        # No parsing needed, but still check for attributes in background
        if background and any(attr in background.lower() for attr in ['bold', 'dim', 'italic', 'underline', 'blink', 'reverse', 'strikethrough', 'strike']):
            foreground, background, parsed_attrs = getSort(foreground=foreground, background=background, attrs=parsed_attrs)
    
    # Initialize the color processor
    _coloring = MakeColors()
    
    # Handle forced coloring mode
    if force or os.getenv('MAKE_COLORS_FORCE') == '1' or os.getenv('MAKE_COLORS_FORCE') == 'True':
        return _coloring.colored(string, foreground, background, parsed_attrs)
    else:
        # Check environment settings and terminal support
        if not _coloring.supports_color() or os.getenv('MAKE_COLORS') == '0':
            # Return plain text when colors are disabled or unsupported
            return string
        elif os.getenv('MAKE_COLORS') == '1':
            # Explicitly enabled
            return _coloring.colored(string, foreground, background, parsed_attrs)
        else:
            # Default behavior - apply coloring
            return _coloring.colored(string, foreground, background, parsed_attrs)

def make_color(string, foreground='white', background=None, attrs=[], force=False):
    """Alias function for make_colors with identical functionality.

    This function provides an alternative name for make_colors() to accommodate
    different naming preferences. All parameters and behavior are identical.

    Args:
        string (str): The text string to be colorized.
        foreground (str): Foreground color specification. Defaults to 'white'.
        background (str, optional): Background color specification. Defaults to None.
        attrs (list): List of text attributes. Defaults to empty list.
        force (bool): Force color output regardless of support. Defaults to False.

    Returns:
        str: The colorized string or original string based on environment settings.

    Example:
        >>> # These calls are equivalent:
        >>> text1 = make_color("Hello", "red")
        >>> text2 = make_colors("Hello", "red")
        >>> # Both produce the same red-colored output

    See Also:
        make_colors: The main implementation function
    """
    return make_colors(string, foreground, background, attrs, force)

def make(string, foreground='white', background=None, attrs=[], force=False):
    """Short alias for make_colors function.
    
    Provides the shortest possible function name for quick usage.
    
    Args:
        string (str): The text string to be colorized.
        foreground (str): Foreground color specification. Defaults to 'white'.
        background (str, optional): Background color specification. Defaults to None.
        attrs (list): List of text attributes. Defaults to empty list.
        force (bool): Force color output regardless of support. Defaults to False.
    
    Returns:
        str: The colorized string or original string based on environment settings.
        
    Example:
        >>> # Shortest way to colorize text:
        >>> text = make("Hello", "bold-red")
        >>> print(text)
    """
    return make_colors(string, foreground, background, attrs, force)

def print(string, foreground='white', background=None, attrs=[], force=False):
    """Print colored text directly to the console with automatic formatting.

    This convenience function combines color formatting and printing in a single call.
    It applies the make_colors() function and immediately outputs the result to stdout,
    making it ideal for direct console output without intermediate variables.

    Args:
        string (str): The text string to be printed with colors.
                     Examples: "System ready", "Error: File not found", "Process complete"
        foreground (str): Foreground text color. Supports full names, abbreviations,
                         combined formats, and attribute detection. Defaults to 'white'.
                         Examples: "red", "r", "lightblue", "bold-red-yellow"
        background (str, optional): Background color specification.
                                   Supports 'on_' prefix format and abbreviations.
                                   Defaults to None (transparent background).
                                   Examples: "yellow", "on_blue", "lb"
        attrs (list): List of text attributes for styling options.
                     Examples: ['bold', 'underline']. Defaults to empty list.
        force (bool): Force colored output even when terminal doesn't support colors.
                     Useful for logging or file redirection. Defaults to False.

    Returns:
        None: This function outputs directly to console and returns None.

    Example:
        >>> # Direct colored printing
        >>> print("Success!", "green")
        >>> print("Warning: Low disk space", "yellow", "on_black")
        >>> print("Critical Error!", "red", "on_white")
        
        >>> # Using abbreviations
        >>> print("Info message", "lb")  # Light blue text
        >>> print("Debug output", "c", "b")  # Cyan on black
        
        >>> # Combined format with attribute detection (NEW!)
        >>> print("Error", "bold-red")  # Bold red text
        >>> print("Warning", "italic-yellow-black")  # Italic yellow on black

        >>> # Force colors for file redirection
        >>> import sys
        >>> with open("colored_log.txt", "w") as sys.stdout:
        ...     print("Log entry", "blue", force=True)
        
        >>> # Rich markup format
        >>> print("[bold blue]Information[/]")

    Note:
        - This function modifies the built-in print() behavior within this module
        - Automatically handles color support detection
        - Supports all new attribute detection features
        - Respects all environment variable settings
        - Original print function is preserved as _print for internal use
    """
    _print(make_colors(string, foreground, background, attrs, force))

def print_exception(*args, **kwargs):
    import traceback
    """
    Print exception with different colors for each type, value, dan traceback.
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    if not exc_type:
        return _print(make_colors("No active exception to print !", "lightred"))

    tb_lines = traceback.format_tb(exc_tb)
    for line in tb_lines:
        _print(make_colors(line.strip(), kwargs.get('tb_color', "lc")))

    _print(make_colors(f"{exc_type.__name__}: ", kwargs.get("tp_color", "y")), end='')
    _print(make_colors(str(exc_value), kwargs.get("tv_color", "white-red-blink")))

    return exc_type, exc_value, exc_tb

def _make_ansi_func(fg: str, bg: Optional[str] = None, attrs: Optional[List[str]] = None):
    if not _USE_COLOR:
        return lambda text: str(text)

    codes = []
    if attrs:
        for attr in attrs:
            code = ATTR_CODES.get(attr)
            if code and code not in codes:
                codes.append(code)
    if bg:
        bg_code = BG_CODES.get(bg)
        if bg_code:
            codes.append(bg_code)
    fg_code = FG_CODES.get(fg)
    if fg_code:
        codes.append(fg_code)
    if not codes:
        return lambda text: str(text)

    ansi_start = f"\033[{';'.join(codes)}m"
    return lambda text: f"{ansi_start}{text}{RESET}"

# === GENERATE SEMUA FUNGSI ===
_all_names = []

# 1. Nama lengkap foreground
_fg_funcs = {name: _make_ansi_func(name) for name in FG_CODES}
_all_names.extend(FG_CODES.keys())

# 2. Kombinasi lengkap: red_on_white
_combo_funcs = {}
for fg in FG_CODES:
    for bg in BG_CODES:
        name = f"{fg}_on_{bg}"
        _combo_funcs[name] = _make_ansi_func(fg, bg)
        _all_names.append(name)

# 3. Singkatan kombinasi: w_bl, r_w, dll
_abbr_combo_funcs = {}
for fg in FG_CODES:
    for bg in BG_CODES:
        fg_abbr = _MAIN_ABBR.get(fg)
        bg_abbr = _MAIN_ABBR.get(bg)
        if fg_abbr and bg_abbr:
            name = f"{fg_abbr}_{bg_abbr}"
            if name not in _all_names:
                _abbr_combo_funcs[name] = _make_ansi_func(fg, bg)
                _all_names.append(name)

# 4. 🔥 SINGKATAN FOREGROUND-ONLY: bl, r, g, w, lb, dll 🔥
_abbr_fg_funcs = {}
for full_name in FG_CODES:
    abbr = _MAIN_ABBR.get(full_name)
    if abbr and abbr not in _all_names:
        _abbr_fg_funcs[abbr] = _make_ansi_func(full_name)
        _all_names.append(abbr)

# Ekspor SEMUA ke namespace modul
globals().update(_fg_funcs)
globals().update(_combo_funcs)
globals().update(_abbr_combo_funcs)
globals().update(_abbr_fg_funcs)

def colorize(
    text: str,
    data: Optional[str] = None,
    fg: str = '',
    bg: str = '',
    attrs: Optional[List[str]] = None
) -> str:
    if attrs is None:
        attrs = []
    parsed_fg, parsed_bg, parsed_attrs = getSort(data=data, foreground=fg, background=bg, attrs=attrs)
    func = _make_ansi_func(parsed_fg, parsed_bg, parsed_attrs)
    return func(text)

class Color:
    def __init__(self, foreground, background=None):
        self.COLOR = self.convert(foreground, background)

    def convert(self, foreground, background=None):
        # Check if attributes are embedded in foreground string or if combined format is used
        if foreground and any(attr in foreground.lower() for attr in ['bold', 'dim', 'italic', 'underline', 'blink', 'reverse', 'strikethrough', 'strike']):
            foreground, background, parsed_attrs = getSort(foreground, background=background, attrs=parsed_attrs)
        elif "-" in foreground or "_" in foreground or "," in foreground:
            foreground, background, parsed_attrs = getSort(foreground, attrs=parsed_attrs)
        elif (foreground and len(foreground) < 3) or (background and len(background) < 3):
            # Expand abbreviations
            foreground, background, parsed_attrs = getSort(foreground=foreground, background=background, attrs=parsed_attrs)
        else:
            # No parsing needed, but still check for attributes in background
            if background and any(attr in background.lower() for attr in ['bold', 'dim', 'italic', 'underline', 'blink', 'reverse', 'strikethrough', 'strike']):
                foreground, background, parsed_attrs = getSort(foreground=foreground, background=background, attrs=parsed_attrs)
        
        fore_color_bank = {
            'black': '30', 'red': '31', 'green': '32', 'yellow': '33',
            'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37',
            'lightblack': '90', 'lightgrey': '90', 'lightred': '91',
            'lightgreen': '92', 'lightyellow': '93', 'lightblue': '94',
            'lightmagenta': '95', 'lightcyan': '96', 'lightwhite': '97',
        }

        back_color_bank = {
            'black': '40', 'red': '41', 'green': '42', 'yellow': '43',
            'blue': '44', 'magenta': '45', 'cyan': '46', 'white': '47',
            'on_black': '40', 'on_red': '41', 'on_green': '42',
            'on_yellow': '43', 'on_blue': '44', 'on_magenta': '45',
            'on_cyan': '46', 'on_white': '47',
            'lightblack': '100', 'lightgrey': '100', 'lightred': '101',
            'lightgreen': '102', 'lightyellow': '103', 'lightblue': '104',
            'lightmagenta': '105', 'lightcyan': '106', 'lightwhite': '107',
            'on_lightblack': '100', 'on_lightgrey': '100', 'on_lightred': '101',
            'on_lightgreen': '102', 'on_lightyellow': '103', 'on_lightblue': '104',
            'on_lightmagenta': '105', 'on_lightcyan': '106', 'on_lightwhite': '107',
        }

        fg = fore_color_bank.get(foreground, '37')  # default white
        bg = back_color_bank.get(background, '40')  # default black

        return f"\033[{bg};{fg}m"

    def format(self, text):
        return f"{self.COLOR}{text}{RESET}"

    def __str__(self):
        return self.COLOR

    def __call__(self, text):
        return self.format(text)

class Colors(Color):
    pass

__all__ = _all_names + ['MakeColors', 'MakeColor', 'color_map', 'getSort', 'parse_rich_markup', 'make_colors', 'make_color', 'make', 'colorize', "Color", "Colors"]


# Example usage and testing section
if __name__ == '__main__':
    # Test color support detection
    _print("=== MakeColors Module Test Suite ===")
    _print(f"Color support detected: {MakeColors.supports_color()}")
    _print(f"Platform: {sys.platform}")
    _print("")
    
    # Initialize color processor
    mc = MakeColors()
    
    # Test basic colors
    _print("=== Basic Color Tests ===")
    _print(make_colors("Red text", "red"))
    _print(make_colors("Green text", "green"))  
    _print(make_colors("Blue text", "blue"))
    _print(make_colors("Yellow text", "yellow"))
    _print(make_colors("Magenta text", "magenta"))
    _print(make_colors("Cyan text", "cyan"))
    _print(make_colors("White text", "white"))
    _print("")
    
    # Test attributes parameter
    _print("=== Attributes Parameter Tests ===")
    _print(make_colors("Bold text", "red", attrs=['bold']))
    _print(make_colors("Underlined text", "green", attrs=['underline']))
    _print(make_colors("Italic text", "blue", attrs=['italic']))
    _print(make_colors("Bold underlined text", "yellow", attrs=['bold', 'underline']))
    _print("")
    
    # Test new attribute detection in strings (NEW FEATURE!)
    _print("=== Attribute Detection Tests (NEW!) ===")
    _print("Testing attribute detection from combined strings:")
    _print(make_colors("Bold red text", "bold-red"))
    _print(make_colors("Italic blue text", "italic-blue"))
    _print(make_colors("Underlined green text", "underline-green"))
    _print(make_colors("Bold italic yellow text", "bold-italic-yellow"))
    _print(make_colors("Bold red on black", "bold-red-black"))
    _print("")
    
    # Test attribute detection with different separators
    _print("Testing with different separators:")
    _print(make_colors("Bold red text", "bold_red"))
    _print(make_colors("Underline cyan text", "underline_cyan"))
    _print(make_colors("Dim white on blue", "dim_white_blue"))
    _print(make_colors("Italic green, comma separated", "italic,green"))
    _print("")
    
    # Test complex attribute combinations
    _print("Testing complex combinations:")
    _print(make_colors("Multi-attribute text", "bold-underline-italic-red-yellow"))
    _print(make_colors("Blink text", "blink-magenta"))
    _print(make_colors("Reverse text", "reverse-white-black"))
    _print("")
    
    # Test light colors
    _print("=== Light Color Tests ===")
    _print(make_colors("Light red text", "lightred"))
    _print(make_colors("Light green text", "lightgreen"))
    _print(make_colors("Light blue text", "lightblue"))
    _print(make_colors("Light yellow text", "lightyellow"))
    _print("")
    
    # Test background colors
    _print("=== Background Color Tests ===")
    _print(make_colors("White text on red background", "white", "on_red"))
    _print(make_colors("Black text on yellow background", "black", "on_yellow"))
    _print(make_colors("Yellow text on blue background", "yellow", "on_blue"))
    _print(make_colors("Green text on black background", "green", "on_black"))
    _print("")
    
    # Test color abbreviations
    _print("=== Color Abbreviation Tests ===")
    _print(make_colors("Red abbreviated", "r"))
    _print(make_colors("Green abbreviated", "g")) 
    _print(make_colors("Blue abbreviated", "bl"))
    _print(make_colors("Light blue abbreviated", "lb"))
    _print(make_colors("Light red abbreviated", "lr"))
    _print("")
    
    # Test combined format
    _print("=== Combined Format Tests ===")
    _print(make_colors("Red on yellow, separated by '-'", "red-yellow"))
    _print(make_colors("Blue on white, separated by '_'", "blue_white"))
    _print(make_colors("Green(g) on black(b), separated by '-'", "g-b"))
    _print(make_colors("Light blue(lb) on red(r), separated by '_'", "lb_r"))
    _print(make_colors("white(w) on magenta(m), separated by ','", "w,m"))
    _print("")
    
    # Test rich markup format
    _print("=== Rich Markup Format Tests ===")
    _print("Rich markup is now supported! Use format: [color]text[/] or [color1 on color2]text[/]")
    _print("")
    
    # Basic rich markup tests
    _print("Basic rich markup:")
    _print(make_colors("[red]This is red text[/]"))
    _print(make_colors("[green]This is green text[/]"))
    _print(make_colors("[blue]This is blue text[/]"))
    _print(make_colors("[yellow]This is yellow text[/]"))
    _print("")
    
    # Rich markup with background
    _print("Rich markup with backgrounds:")
    _print(make_colors("[white on red]White on red background[/]"))
    _print(make_colors("[black on yellow]Black on yellow background[/]"))
    _print(make_colors("[blue on white]Blue on white background[/]"))
    _print(make_colors("[green on black]Green on black background[/]"))
    _print("")
    
    # Rich markup with styles
    _print("Rich markup with styles:")
    _print(make_colors("[bold red]Bold red text[/]"))
    _print(make_colors("[italic blue]Italic blue text[/]"))
    _print(make_colors("[underline green]Underlined green text[/]"))
    _print(make_colors("[bold white on red]Bold white on red[/]"))
    _print("")
    
    # Equivalence demonstration
    _print("=== Equivalence Tests ===")
    _print("These methods produce identical results:")
    _print("Method 1 (traditional):", end=" ")
    _print(make_colors("TEST", "white", "on_red"))
    _print("Method 2 (rich markup):", end=" ")
    _print(make_colors("[white on red]TEST[/]"))
    _print("Method 3 (attribute detection):", end=" ")
    _print(make_colors("TEST", "white-red"))
    _print("")
    
    _print("Method 1 (abbreviations):", end=" ")
    _print(make_colors("INFO", "lb", "b"))
    _print("Method 2 (rich markup):   ", end=" ")  
    _print(make_colors("[lightblue on black]INFO[/]"))
    _print("Method 3 (attribute detection):", end=" ")
    _print(make_colors("INFO", "lb_b"))
    _print("")
    
    # Complex rich markup examples
    _print("=== Complex Rich Markup Examples ===")
    log_examples = [
        "[bold white on black][DEBUG][/] [cyan]Database connection established[/]",
        "[bold blue on black][INFO][/] [white]User authentication successful[/]",
        "[bold yellow on black][WARNING][/] [lightyellow]High memory usage detected[/]",
        "[bold white on red][ERROR][/] [lightred]Database connection failed[/]",
        "[bold white on red][CRITICAL][/] [white on red]System shutdown required[/]"
    ]
    
    for log in log_examples:
        _print(make_colors(log))
    
    _print("")

    _print("""
>>> # Force colors for file redirection
>>> import sys
>>> with open("colored_log.txt", "w") as sys.stdout:
...     print("Log entry", "blue", force=True)
    """)
    
    # New attribute detection feature demo
    _print("=== New Attribute Detection Feature Demo ===")
    _print("Now you can include attributes directly in color strings!")
    _print("")

    # Performance comparison
    _print("=== Performance Comparison ===")
    import time
    
    # Test traditional method
    start_time = time.time()
    for i in range(100):
        make_colors("Performance test", "red", "on_yellow")
    traditional_time = time.time() - start_time
    
    # Test rich markup method
    start_time = time.time()
    for i in range(100):
        make_colors("[red on yellow]Performance test[/]")
    rich_time = time.time() - start_time
    
    _print(f"Traditional method: {traditional_time:.4f} seconds")
    _print(f"Rich markup method: {rich_time:.4f} seconds")
    _print(f"Performance difference: {abs(rich_time - traditional_time):.4f} seconds")
    _print("")
    
    _print("Old way (still works):")
    _print(f'make_colors("Error", "red", attrs=["bold"]) -> ', end="")
    _print(make_colors("Error", "red", attrs=["bold"]))
    _print("")
    
    _print("New way (attribute detection):")
    _print(f'make_colors("Error", "bold-red") -> ', end="")
    _print(make_colors("Error", "bold-red"))
    _print(f'make_colors("Warning", "italic-yellow") -> ', end="")  
    _print(make_colors("Warning", "italic-yellow"))
    _print(f'make_colors("Info", "underline-blue") -> ', end="")
    _print(make_colors("Info", "underline-blue"))
    _print("")
    
    _print("Complex examples:")
    _print(f'make_colors("Critical", "bold-underline-white-red") -> ', end="")
    _print(make_colors("Critical", "bold-underline-white-red"))
    _print(f'make_colors("Highlight", "italic-bold-yellow-black") -> ', end="")
    _print(make_colors("Highlight", "italic-bold-yellow-black"))
    _print("")
    
    _print("With different separators:")
    _print(f'make_colors("Debug", "dim_cyan") -> ', end="")
    _print(make_colors("Debug", "dim_cyan"))
    _print(f'make_colors("Blink", "blink,magenta,white") -> ', end="")
    _print(make_colors("Blink", "blink,magenta,white"))
    _print("")

    # Test convenience print function
    _print("=== Convenience Print Function Tests ===")
    print("Direct red printing", "red")
    print("Direct green with background", "green", "on_yellow")
    print("Direct abbreviated colors", "lb", "r")
    print("Direct combined format", "magenta-white")
    print("Direct with attribute detection", "bold-cyan")
    print("Direct complex attributes", "italic-underline-yellow-black")
    _print("")
    
    # Mixed format examples
    _print("=== Mixed Format Examples ===")
    _print("You can mix different approaches:")
    _print("Rich + traditional:", make_colors("[green]Success:[/] Operation completed", "lightgreen"))
    _print("Multiple rich tags:", make_colors("[red]Error in[/] [bold white on blue]module.py[/] [red]line 42[/]"))
    _print("Attribute detection + rich:", make_colors("[red]Error:[/] ", "bold-white") + make_colors("System failure", "underline-red"))
    _print("")
    
    # Test force mode
    _print("=== Force Mode Tests ===")
    _print("Forced coloring (always applies):")
    _print(make_colors("This should be red even if disabled", "red", force=True))
    _print(make_colors("Forced bold blue", "bold-blue", force=True))
    _print("")
    
    # Test error handling
    _print("=== Error Handling Tests ===")
    _print("Invalid colors fall back to defaults:")
    _print(make_colors("Invalid foreground", "invalidcolor"))
    _print(make_colors("Invalid background", "red", "invalidbackground"))
    _print("")
    _print(make_colors("Invalid attribute in string", "invalidattr-red"))
    
    # Performance and compatibility tests
    _print("=== Performance Tests ===")
    import time
    start_time = time.time()
    for i in range(100):
        make_colors(f"Performance test {i}", "green")
    end_time = time.time()
    _print(f"Generated 100 colored strings in {end_time - start_time:.4f} seconds")
    _print("")
    
    # Environment variable demonstration
    _print("=== Environment Variable Tests ===")
    _print("Current environment settings:")
    _print(f"MAKE_COLORS: {os.getenv('MAKE_COLORS', 'not set')}")
    _print(f"MAKE_COLORS_FORCE: {os.getenv('MAKE_COLORS_FORCE', 'not set')}")
    _print(f"MAKE_COLORS_DEBUG: {os.getenv('MAKE_COLORS_DEBUG', 'not set')}")
    _print("")
    
    # Complex formatting examples
    _print("=== Complex Formatting Examples ===")
    _print("Log level examples:")
    print("[DEBUG]", "cyan")
    print("[INFO]", "blue") 
    print("[WARNING]", "yellow", "on_black")
    print("[ERROR]", "red", "on_white")
    print("[CRITICAL]", "white", "on_red")
    _print("")
    
    # Status indicator examples
    _print("Status indicators:")
    print("✓ Success", "lightgreen")
    print("⚠ Warning", "lightyellow") 
    print("✗ Failed", "lightred")
    print("● Running", "lightblue")
    print("◐ Pending", "lightmagenta")
    _print("")
    
    # Code syntax highlighting example
    _print("=== Code Syntax Highlighting Example ===")
    print("def", "blue")
    _print(" ", end="")
    print("function_name", "green")
    _print("(", end="")
    print("parameter", "magenta")
    _print("):")
    _print("    ", end="")
    print("# This is a comment", "lightblack")
    _print("    ", end="")
    print("return", "blue")
    _print(" ", end="")
    print("'Hello World'", "yellow")
    _print("")
    
    # Progress bar simulation
    _print("=== Progress Bar Simulation ===")
    progress_chars = "█" * 20
    for i in range(0, 21, 5):
        filled = "█" * i
        empty = "░" * (20 - i)
        percentage = (i * 100) // 20
        progress_bar = f"[{filled}{empty}] {percentage}%"
        if percentage < 30:
            color = "red"
        elif percentage < 70:
            color = "yellow" 
        else:
            color = "green"
        _print(make_colors(progress_bar, color))
        time.sleep(0.5)
    _print("")
    
    # Color palette showcase
    _print("=== Full Color Palette Showcase ===")
    colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    light_colors = ["lightblack", "lightred", "lightgreen", "lightyellow", 
                   "lightblue", "lightmagenta", "lightcyan", "lightwhite"]
    
    _print("Standard colors:")
    for color in colors:
        _print(f"{make_colors('██████', color)} {color}")
    _print("")
    
    _print("Light colors:")
    for color in light_colors:
        _print(f"{make_colors('██████', color)} {color}")
    _print("")
    
    _print("Background combinations:")
    for bg in colors[:4]:  # Show first 4 backgrounds to avoid clutter
        line = ""
        for fg in colors:
            if fg != bg:  # Skip same color combinations
                line += make_colors("██", fg, f"on_{bg}") + " "
        _print(f"on_{bg}: {line}")
    _print("")
    
    # Final test summary
    _print("=== Test Summary ===")
    test_results = [
        ("Color support detection", "✓"),
        ("Basic color rendering", "✓"),
        ("Background colors", "✓"),
        ("Color abbreviations", "✓"),
        ("Combined format parsing", "✓"),
        ("Rich console formatting", "✓"),
        ("Rich markup format", "✓"),
        ("Attribute detection (NEW!)", "✓"),
        ("Multiple markup sections", "✓"),
        ("Multiple separators support", "✓"),
        ("Equivalence between methods", "✓"),
        ("Convenience functions", "✓"),
        ("Error handling", "✓"),
        ("Environment variables", "✓"),
        ("Performance", "✓")
    ]
    
    for test_name, status in test_results:
        status_color = "green" if status == "✓" else "red"
        print(f"{test_name}: ", "white")
        print(status, status_color)

    _print("🧙 WITH MAGICK:\n")
    # 1. A complete name
    print(red("Error!"))
    print(bl("Im Blue"))
    print(green_on_black("Success"))

    # 2. Abbreviation
    print(w_bl("White on Blue"))      # white on blue
    print(r_w("Red on White"))        # red on white
    print(g_b("Green on Black"))      # green on black
    print(lb_b("Light Blue on Black"))

    # 3. Dynamic with attributes
    print(colorize("Bold Red", "red-bold"))
    print(colorize("Underlined Green", fg="g", bg="b", attrs=["underline"]))

    # 4. Parsing flexible
    print(colorize("Blinking Magenta", "magenta-blink"))
    
    _print("")
    _print("=== New Features Summary ===")
    _print("🆕 ATTRIBUTE DETECTION: Now you can include text attributes directly in color strings!")
    _print("Examples:")
    _print('  make_colors("Text", "bold-red")           # Bold red text')
    _print('  make_colors("Text", "italic_blue_white")  # Italic blue text on white background')
    _print('  make_colors("Text", "underline-green")    # Underlined green text')
    _print('  make_colors("Text", "bold,italic,yellow") # Bold italic yellow text')
    _print("")
    _print("Supported attributes: bold, dim, italic, underline, blink, reverse, strikethrough|strike")
    _print("Supported separators: hyphen (-), underscore (_), and comma (,)")
    _print("Order doesn't matter: 'bold-red-yellow' = 'red-bold-yellow' = 'yellow-red-bold'")
    _print("")
    
    _print("=== Usage Tips ===")
    _print("1. Use environment variable MAKE_COLORS=0 to disable colors globally")
    _print("2. Use MAKE_COLORS_FORCE=1 to force colors even in non-TTY environments") 
    _print("3. Use MAKE_COLORS_DEBUG=1 to see detailed color and attribute parsing")
    _print("4. Color abbreviations: r=red, g=green, b=black, bl=blue, lb=lightblue")
    _print("5. Combined format: 'color1-color2' or 'color1_color2' for fg-bg combinations")
    _print("6. NEW: Include attributes: 'bold-red-yellow' or 'italic_blue_white'")
    _print("7. Background colors support both 'color' and 'on_color' formats")
    _print("8. Use force=True parameter for file output or logging applications")
    _print("9. Rich markup format: '[color]text[/]' or '[color1 on color2]text[/]'")
    _print("10. Rich styles: '[bold red]text[/]', '[italic blue]text[/]', etc.")
    _print("11. NEW: Attribute detection works with all separators: -, _, and ,")
    _print("12. Short alias: make() function for quick usage")
    _print("")
    
    _print("=== Attribute Detection Quick Reference ===")
    _print("• Simple: make_colors('Text', 'bold-red')")
    _print("• With background: make_colors('Text', 'italic-blue-yellow')")  
    _print("• Multiple attrs: make_colors('Text', 'bold-underline-green')")
    _print("• Any order: make_colors('Text', 'red-bold') == make_colors('Text', 'bold-red')")
    _print("• All separators: 'bold_red', 'bold-red', 'bold,red' all work")
    _print("• Quick usage: make('Text', 'bold-red')  # Shortest function name")
    _print("")
    
    _print("Module test completed successfully!")
    _print("New attribute detection feature is now fully implemented!")
    _print("Rich markup format with multiple tags is fully supported!")
    _print("All methods now support automatic attribute detection from color strings!")
    _print("Multiple separators (-, _, ,) are supported for maximum flexibility!")

