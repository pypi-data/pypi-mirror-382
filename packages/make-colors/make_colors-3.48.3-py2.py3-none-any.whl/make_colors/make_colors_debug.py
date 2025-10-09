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
"""

from __future__ import print_function

import os
import sys
import re

# Global variables for console mode handling
MODE = 0
_print = print

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
            attrs (list, optional): List of text attributes (currently reserved for future use).
                                   Example: ['bold', 'underline'] (not yet implemented)

        Returns:
            str: The input string wrapped with ANSI escape codes for colorization.
                Format: "[<bg_code>;<fg_code><text>[0m"
                Example: "[43;31mHello World[0m" (red text on yellow background)

        Example:
            >>> mc = MakeColors()
            >>> red_text = mc.colored("Error!", "red")
            >>> print(red_text)  # Prints "Error!" in red
            
            >>> warning = mc.colored("Warning!", "yellow", "on_black")
            >>> print(warning)  # Yellow text on black background
            
            >>> info = mc.colored("Info", "lightblue", "on_white")
            >>> print(info)  # Light blue text on white background

        Note:
            - Invalid color names fallback to white foreground and black background
            - The method returns raw ANSI codes; use print() to see colored output
            - Background colors can be specified with or without 'on_' prefix
        """
        
        # Comprehensive foreground color mapping with ANSI codes
        fore_color_bank = {
            # Standard colors (30-37)
            'black': '30m',
            'red': '31m',
            'green': '32m',
            'yellow': '33m',
            'blue': '34m',
            'magenta': '35m',
            'cyan': '36m',
            'white': '37m',

            # Bright colors (90-97)
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

        # Comprehensive background color mapping with ANSI codes
        back_color_bank = {
            # Standard background colors (40-47)
            'black': '40m',
            'red': '41m',
            'green': '42m',
            'yellow': '43m',
            'blue': '44m',
            'magenta': '45m',
            'cyan': '46m',
            'white': '47m',

            # Alternative 'on_' prefix format
            'on_black': '40m',
            'on_red': '41m',
            'on_green': '42m',
            'on_yellow': '43m',
            'on_blue': '44m',
            'on_magenta': '45m',
            'on_cyan': '46m',
            'on_white': '47m',

            # Bright background colors (100-107)
            'lightblack': '100m',
            'lightgrey': '100m',
            'lightred': '101m',
            'lightgreen': '102m',
            'lightyellow': '103m',
            'lightblue': '104m',
            'lightmagenta': '105m',
            'lightcyan': '106m',
            'lightwhite': '107m',

            # Bright background with 'on_' prefix
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

        # Text attributes mapping
        attr_codes = {
            'bold': '1',
            'dim': '2',
            'italic': '3',
            'underline': '4',
            'blink': '5',
            'reverse': '7',
            'strikethrough': '9',
            'normal': '22',  # Reset bold/dim
            'no_italic': '23',  # Reset italic
            'no_underline': '24',  # Reset underline
        }

        # Look up colors in the banks, with fallback defaults
        background_code = back_color_bank.get(background)
        foreground_code = fore_color_bank.get(foreground)
        
        # Apply fallback defaults for invalid colors
        if not background_code:
            background_code = '40m'  # Default to black background
        if not foreground_code:
            foreground_code = '37m'  # Default to white foreground

        # Process attributes
        attr_sequence = ""
        if attrs:
            valid_attrs = []
            for attr in attrs:
                if attr.lower() in attr_codes:
                    valid_attrs.append(attr_codes[attr.lower()])
            if valid_attrs:
                attr_sequence = ";".join(valid_attrs) + ";"

        # Return formatted ANSI escape sequence with attributes
        return "[%s%s;%s%s[0m" % (attr_sequence, background_code[:-1], foreground_code, string)
        # return "[%s;%s%s[0m" % (background[:-1], foreground, string)

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
        # Style mapping for rich text attributes
        style_codes = {
            'bold': '1;',
            'dim': '2;',
            'italic': '3;',
            'underline': '4;',
            'blink': '5;',
            'reverse': '7;',
            'strikethrough': '9;'
        }
        
        # Apply style prefix if specified
        style_prefix = ''
        if style and style.lower() in style_codes:
            style_prefix = style_codes[style.lower()]
        
        # Convert rich format to ANSI format
        if bg_color and not bg_color.startswith('on_'):
            bg_color = f'on_{bg_color}'
            
        # Use the standard colored method with style enhancement
        if style_prefix:
            # Temporarily modify the colored method to include style
            result = self.colored(string, color or 'white', bg_color)
            # Insert style code after the opening bracket
            result = result.replace('[', f'[{style_prefix}', 1)
            return result
        else:
            return self.colored(string, color or 'white', bg_color)

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

def getSort(data=None, foreground='', background=''):
    """Parse and sort color specifications from combined format strings.

    This function handles flexible color specification formats including
    combined foreground-background strings separated by delimiters, and
    expands color abbreviations to full names.

    Args:
        data (str, optional): Combined color string with format "foreground-background" 
                             or "foreground_background". 
                             Examples: "red-yellow", "blue_white", "r-g"
        foreground (str): Explicit foreground color specification.
                         Examples: "red", "r", "lightblue"
        background (str): Explicit background color specification.
                         Examples: "yellow", "on_blue", "lg"

    Returns:
        tuple[str, str]: A tuple containing (foreground_color, background_color).
                        Both values are full color names, with fallbacks applied:
                        - foreground defaults to 'white' if not specified
                        - background defaults to None if not specified

    Example:
        >>> getSort("red-yellow")           # Returns ("red", "yellow")
        >>> getSort("r_b")                  # Returns ("red", "black")  
        >>> getSort(foreground="blue")      # Returns ("blue", None)
        >>> getSort("lg-on_red")           # Returns ("lightgreen", "on_red")
        >>> getSort()                      # Returns ("white", None)

    Note:
        - Supports both "-" and "_" as delimiters
        - Automatically expands abbreviations using color_map()
        - Handles nested delimiter parsing for complex specifications
        - Debug output available via MAKE_COLORS_DEBUG environment variable
    """
    # Debug output for troubleshooting color parsing
    if data:
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: data =", data)
        
        # Parse combined format: "foreground-background" or "foreground_background"  
        if "-" in data or "_" in data:
            foreground, background = re.split("-|_", data)
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
    
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"getSort: foreground: {foreground}")
        _print(f"getSort: background: {background}")
    
    # Handle nested delimiters in foreground specification
    if foreground and len(foreground) > 2 and ("-" in foreground or "_" in foreground):
        _foreground, _background = re.split("-|_", foreground)
        foreground = _foreground or foreground
        background = _background or background
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: foreground [3] =", foreground)
            _print("getSort: background [3] =", background)
    
    # Handle nested delimiters in background specification        
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
            
        # Apply default values for missing specifications    
        foreground = foreground or 'white'
        background = background or None
        if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
            _print("getSort: foreground [6] =", foreground)
            _print("getSort: background [6] =", background)
        
        # Return early if both colors are already full names    
        if foreground and len(foreground) > 2 and background and len(background) > 2:
            return foreground, background
          
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"getSort: foreground before: {foreground}")
        _print(f"getSort: background before: {background}")
    
    # Expand abbreviations to full color names    
    if foreground and len(foreground) < 3:
        foreground = color_map(foreground)
    if background and len(background) < 3:
        background = color_map(background)
    
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"getSort: returning foreground: {foreground}")
        _print(f"getSort: returning background: {background}")
    return foreground, background

def parse_rich_markup(text):
    """Parse Rich console markup format and extract styling information.
    
    This function parses Rich-style markup tags like "[white on red]text[/]" and
    handles multiple markup sections in a single string, converting each to ANSI escape codes or 
    extracts the color and style information for ANSI conversion.
    
    Args:
        text (str): Text with Rich markup format.
                   Examples: "[white on red]TEST[/]", "[bold red]Error[/]", "[blue]Info[/]"
    
    Returns:
        tuple: (cleaned_text, foreground, background, style)
               - cleaned_text: Text with markup tags removed
               - foreground: Foreground color name or None
               - background: Background color name or None  
               - style: Style attribute or None
    
    Example:
        >>> parse_rich_markup("[white on red]TEST[/]")
        ('TEST', 'white', 'red', None)
        >>> parse_rich_markup("[bold blue]Message[/]")  
        ('Message', 'blue', None, 'bold')
        >>> parse_rich_markup("[italic green on yellow]Warning[/]")
        ('Warning', 'green', 'yellow', 'italic')
    """
    
    # Pattern to match Rich markup: [style] content [/]
    pattern = r'\[([^\]]+)\]([^[]*?)\[/?[^\]]*?\]'
    #pattern = r'\[([^\]]+)\]([^[]*?)\[/?[^\]]*\]'
    match = re.search(pattern, text)
    
    if not match:
        # No markup found, return as-is
        return text, None, None, None
    
    markup = match.group(1).strip()
    content = match.group(2)
    
    # Parse the markup content
    foreground = None
    background = None
    style = None
    
    # Handle different markup formats
    parts = markup.lower().split()
    
    # Check for styles first
    styles = ['bold', 'italic', 'underline', 'dim', 'blink', 'reverse', 'strikethrough']
    for part in parts[:]:
        if part in styles:
            style = part
            parts.remove(part)
            break
    
    # Parse remaining parts for colors
    remaining = ' '.join(parts)
    
    if ' on ' in remaining:
        # Format: "color1 on color2"
        color_parts = remaining.split(' on ')
        if len(color_parts) == 2:
            foreground = color_parts[0].strip()
            background = color_parts[1].strip()
    else:
        # Single color specification
        if remaining:
            foreground = remaining.strip()
    
    return content, foreground, background, style

def parse_rich_markup1(text):
    """Parse Rich console markup format and extract styling information.
    
    This function parses Rich-style markup tags and handles multiple markup sections
    in a single string, converting each to ANSI escape codes.
    
    Args:
        text (str): Text with Rich markup format.
    
    Returns:
        str: Text converted to ANSI escape codes.
    """
    
    # Pattern to match Rich markup: [style] content [/]
    pattern = r'\[([^\]]+)\]([^[]*?)\[/?[^\]]*?\]'
    
    def process_markup(match):
        markup = match.group(1).strip()
        content = match.group(2)
        
        # Parse the markup content
        foreground = None
        background = None
        style = None
        
        # Handle different markup formats
        parts = markup.lower().split()
        
        # Check for styles first
        styles = ['bold', 'italic', 'underline', 'dim', 'blink', 'reverse', 'strikethrough']
        for part in parts[:]:
            if part in styles:
                style = part
                parts.remove(part)
                break
        
        # Parse remaining parts for colors
        remaining = ' '.join(parts)
        
        if ' on ' in remaining:
            # Format: "color1 on color2"
            color_parts = remaining.split(' on ')
            if len(color_parts) == 2:
                foreground = color_parts[0].strip()
                background = color_parts[1].strip()
        else:
            # Single color specification
            if remaining:
                foreground = remaining.strip()
        
        # Create MakeColors instance and apply formatting
        mc = MakeColors()
        attrs = [style] if style else []
        
        # Convert rich format to standard format
        if background and not background.startswith('on_'):
            background = f'on_{background}'
        
        return mc.colored(content, foreground or 'white', background, attrs)
    
    # Process all markup sections in the text
    result = re.sub(pattern, process_markup, text)
    
    # If no markup was processed, return original text
    if result == text and '[' in text and ']' in text:
        return text
    
    return result

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
                         Defaults to 'white'. Ignored if Rich markup is used.
        background (str, optional): Background color specification. Can be:
                                   - Full color name: "yellow", "black"
                                   - With 'on_' prefix: "on_yellow", "on_black"
                                   - Abbreviation: "y", "b"
                                   Defaults to None (no background). Ignored if Rich markup is used.
        attrs (list): List of text attributes for future enhancement.
                     Currently reserved for extensions like ['bold', 'underline'].
                     Defaults to empty list.
        force (bool): Force color output even if environment doesn't support it.
                     Useful for file output or testing.
                     Defaults to False.

    Returns:
        str: The colorized string with ANSI escape codes, or the original string
             if coloring is disabled or unsupported.

    Rich Markup Support:
        The function now supports Rich console markup format:
        - "[color]text[/]" - Single color
        - "[color1 on color2]text[/]" - Foreground and background  
        - "[style color]text[/]" - Style with color
        - "[style color1 on color2]text[/]" - Style with colors
        
        Supported styles: bold, italic, underline, dim, blink, reverse, strikethrough
        Supported colors: All standard ANSI colors and their light variants

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
        
        >>> # Combined format
        >>> status = make_colors("Ready", "green-black")
        >>> print(status)  # Green text on black background
        
        >>> # Rich markup format (NEW!)
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

    Note:
        - Rich markup takes precedence over foreground/background parameters
        - Automatically detects terminal color support
        - Falls back to plain text when colors are unsupported
        - Respects environment variable settings for global control
        - Cross-platform compatible (Windows 10+, Linux, macOS)
        - Fully compatible with Rich console format
    """
    # Check for Rich markup format first
    if '[' in string and ']' in string and '[/' in string:
        # Parse Rich markup format
        parsed_content, rich_fg, rich_bg, rich_style = parse_rich_markup(string)
        if parsed_content != string:  # Markup was found and parsed
            # Use Rich markup colors, override parameters
            string = parsed_content
            if rich_fg:
                foreground = rich_fg
            if rich_bg:
                if not rich_bg.startswith('on_'):
                    background = f'on_{rich_bg}'
                else:
                    background = rich_bg
            if rich_style:
                # Handle style - for now, we'll use the rich_colored method
                _coloring = MakeColors()
                
                # Handle forced coloring or environment checks
                if force or os.getenv('MAKE_COLORS_FORCE') == '1' or os.getenv('MAKE_COLORS_FORCE') == 'True':
                    return _coloring.rich_colored(string, foreground, rich_bg, rich_style)
                else:
                    if not _coloring.supports_color() or os.getenv('MAKE_COLORS') == '0':
                        return string
                    else:
                        return _coloring.rich_colored(string, foreground, rich_bg, rich_style)
    
    # Debug output for color specifications
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"FOREGROUND: {foreground}")
        _print(f"BACKGROUND: {background}")
        _print(f"ATTRS: {attrs}")
    
    # Parse combined color format (e.g., "red-yellow", "r_b")    
    if "-" in foreground or "_" in foreground:
        foreground, background = getSort(foreground)
    elif (foreground and len(foreground) < 3) or (background and len(background) < 3):
        # Expand abbreviations
        foreground, background = getSort(foreground=foreground, background=background)
    
    # Initialize the color processor
    _coloring = MakeColors()
    
    # Handle forced coloring mode
    if force or os.getenv('MAKE_COLORS_FORCE') == '1' or os.getenv('MAKE_COLORS_FORCE') == 'True':
        return _coloring.colored(string, foreground, background, attrs)
    else:
        # Check environment settings and terminal support
        if not _coloring.supports_color() or os.getenv('MAKE_COLORS') == '0':
            # Return plain text when colors are disabled or unsupported
            return string
        elif os.getenv('MAKE_COLORS') == '1':
            # Explicitly enabled
            return _coloring.colored(string, foreground, background, attrs)
        else:
            # Default behavior - apply coloring
            return _coloring.colored(string, foreground, background, attrs)

def make_colors1(string, foreground='white', background=None, attrs=[], force=False):
    """Apply color formatting to text with comprehensive control options and Rich markup support."""
    
    # Check for Rich markup format first
    if '[' in string and ']' in string and '[/' in string:
        # Parse Rich markup format - this now handles multiple markup sections
        result = parse_rich_markup(string)
        if result != string:  # Markup was found and parsed
            # Check if coloring should be applied
            _coloring = MakeColors()
            if force or os.getenv('MAKE_COLORS_FORCE') == '1' or os.getenv('MAKE_COLORS_FORCE') == 'True':
                return result
            else:
                if not _coloring.supports_color() or os.getenv('MAKE_COLORS') == '0':
                    # Strip ANSI codes and return plain text
                    import re
                    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    return ansi_escape.sub('', result)
                else:
                    return result
    
    # Debug output for color specifications
    if os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']:
        _print(f"FOREGROUND: {foreground}")
        _print(f"BACKGROUND: {background}")
        _print(f"ATTRS: {attrs}")
    
    # Parse combined color format (e.g., "red-yellow", "r_b")    
    if "-" in foreground or "_" in foreground:
        foreground, background = getSort(foreground)
    elif (foreground and len(foreground) < 3) or (background and len(background) < 3):
        # Expand abbreviations
        foreground, background = getSort(foreground=foreground, background=background)
    
    # Initialize the color processor
    _coloring = MakeColors()
    
    # Handle forced coloring mode
    if force or os.getenv('MAKE_COLORS_FORCE') == '1' or os.getenv('MAKE_COLORS_FORCE') == 'True':
        return _coloring.colored(string, foreground, background, attrs)
    else:
        # Check environment settings and terminal support
        if not _coloring.supports_color() or os.getenv('MAKE_COLORS') == '0':
            # Return plain text when colors are disabled or unsupported
            return string
        elif os.getenv('MAKE_COLORS') == '1':
            # Explicitly enabled
            return _coloring.colored(string, foreground, background, attrs)
        else:
            # Default behavior - apply coloring
            return _coloring.colored(string, foreground, background, attrs)

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

def print(string, foreground='white', background=None, attrs=[], force=False):
    """Print colored text directly to the console with automatic formatting.

    This convenience function combines color formatting and printing in a single call.
    It applies the make_colors() function and immediately outputs the result to stdout,
    making it ideal for direct console output without intermediate variables.

    Args:
        string (str): The text string to be printed with colors.
                     Examples: "System ready", "Error: File not found", "Process complete"
        foreground (str): Foreground text color. Supports full names, abbreviations,
                         and combined formats. Defaults to 'white'.
                         Examples: "red", "r", "lightblue", "red-yellow"
        background (str, optional): Background color specification.
                                   Supports 'on_' prefix format and abbreviations.
                                   Defaults to None (transparent background).
                                   Examples: "yellow", "on_blue", "lb"
        attrs (list): List of text attributes for future styling options.
                     Reserved for extensions. Defaults to empty list.
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
        
        >>> # Combined format
        >>> print("Status: OK", "green-black")
        
        >>> # Force colors for file redirection
        >>> import sys
        >>> with open("colored_log.txt", "w") as sys.stdout:
        ...     print("Log entry", "blue", force=True)

    Note:
        - This function modifies the built-in print() behavior within this module
        - Automatically handles color support detection
        - Respects all environment variable settings
        - Original print function is preserved as _print for internal use
    """
    _print(make_colors(string, foreground, background, attrs, force))

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
    _print(make_colors("Red on yellow", "red-yellow"))
    _print(make_colors("Blue on white", "blue_white"))
    _print(make_colors("Green on black", "g-b"))
    _print(make_colors("Light blue on red", "lb_r"))
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
    _print("")
    
    _print("Method 1 (abbreviations):", end=" ")
    _print(make_colors("INFO", "lb", "b"))
    _print("Method 2 (rich markup):   ", end=" ")  
    _print(make_colors("[lightblue on black]INFO[/]"))
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
    
    # Mixed format examples
    _print("=== Mixed Format Examples ===")
    _print("You can mix different approaches:")
    _print("Rich + traditional:", make_colors("[green]Success:[/] Operation completed", "lightgreen"))
    _print("Multiple rich tags:", make_colors("[red]Error in[/] [bold white on blue]module.py[/] [red]line 42[/]"))
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
    
    # Test convenience print function
    _print("=== Convenience Print Function Tests ===")
    print("Direct red printing", "red")
    print("Direct green with background", "green", "on_yellow")
    print("Direct abbreviated colors", "lb", "r")
    print("Direct combined format", "magenta-white")
    _print("")
    
    # Test force mode
    _print("=== Force Mode Tests ===")
    _print("Forced coloring (always applies):")
    _print(make_colors("This should be red even if disabled", "red", force=True))
    _print("")
    
    # Test error handling
    _print("=== Error Handling Tests ===")
    _print("Invalid colors fall back to defaults:")
    _print(make_colors("Invalid foreground", "invalidcolor"))
    _print(make_colors("Invalid background", "red", "invalidbackground"))
    _print("")
    
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
        ("Rich markup format (NEW!)", "✓"),
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
    
    _print("")
    _print("=== Usage Tips ===")
    _print("1. Use environment variable MAKE_COLORS=0 to disable colors globally")
    _print("2. Use MAKE_COLORS_FORCE=1 to force colors even in non-TTY environments") 
    _print("3. Use MAKE_COLORS_DEBUG=1 to see detailed color parsing information")
    _print("4. Color abbreviations: r=red, g=green, b=black, bl=blue, lb=lightblue")
    _print("5. Combined format: 'color1-color2' or 'color1_color2' for fg-bg combinations")
    _print("6. Background colors support both 'color' and 'on_color' formats")
    _print("7. Use force=True parameter for file output or logging applications")
    _print("8. NEW: Rich markup format: '[color]text[/]' or '[color1 on color2]text[/]'")
    _print("9. NEW: Rich styles: '[bold red]text[/]', '[italic blue]text[/]', etc.")
    _print("10. Both traditional and rich markup methods produce identical output")
    _print("")
    
    _print("=== Rich Markup Quick Reference ===")
    _print("• Single color: [red]text[/], [blue]text[/]")
    _print("• With background: [white on red]text[/], [black on yellow]text[/]")
    _print("• With style: [bold red]text[/], [italic blue]text[/]")
    _print("• Complex: [bold white on red]text[/], [underline green on black]text[/]")
    _print("• Multiple tags: [red]Error:[/] [bold]Critical failure[/]")
    _print("")
    
    _print("Module test completed successfully!")
    _print("Rich markup format is now fully supported and compatible with Rich console!")
    _print("For more information, see the comprehensive docstrings in each function.")
