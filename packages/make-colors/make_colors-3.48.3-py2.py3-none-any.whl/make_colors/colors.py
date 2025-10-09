# colors.py
import os
import re
import sys
from typing import List, Tuple, Optional

RESET = "\033[0m"
_USE_COLOR = sys.stdout.isatty()
_DEBUG = os.getenv('MAKE_COLORS_DEBUG') in ['1', 'true', 'True']

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

def color_map_colors(color: str) -> str:
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
        elif color == 'lk':
            color = 'lightblack'
        else:
            color = 'lightwhite'
    return color

_MAIN_ABBR = {
    'black': 'b', 'blue': 'bl', 'red': 'r', 'green': 'g',
    'yellow': 'y', 'magenta': 'm', 'cyan': 'c', 'white': 'w',
    'lightblue': 'lb', 'lightred': 'lr', 'lightgreen': 'lg',
    'lightyellow': 'ly', 'lightmagenta': 'lm', 'lightcyan': 'lc',
    'lightwhite': 'lw', 'lightblack': 'lk',
}

def getSort(
    data: Optional[str] = None,
    foreground: str = '',
    background: str = '',
    attrs: Optional[List[str]] = None
) -> Tuple[str, Optional[str], List[str]]:
    if attrs is None:
        attrs = []
    text_attributes = list(ATTR_CODES.keys())
    detected_attrs = attrs.copy()

    def extract_attributes(text: str):
        if not text:
            return text, []
        found_attrs = []
        cleaned_text = text
        for attr in text_attributes:
            if attr in text.lower():
                actual_attr = 'strikethrough' if attr == 'strike' else attr
                found_attrs.append(actual_attr)
                cleaned_text = re.sub(rf'\b{re.escape(attr)}\b', '', cleaned_text, flags=re.IGNORECASE)
                cleaned_text = re.sub(r'[-_,\s]+', ' ', cleaned_text).strip()
        return cleaned_text.strip(), found_attrs

    if data:
        data, data_attrs = extract_attributes(data)
        detected_attrs.extend(data_attrs)
        if any(sep in data for sep in "-_,"):
            parts = [p.strip() for p in re.split(r"[-_,]", data) if p.strip()]
            if len(parts) >= 2:
                foreground, background = parts[0], parts[1]
            elif len(parts) == 1:
                foreground = parts[0]
        else:
            foreground = data

    if foreground:
        foreground, fg_attrs = extract_attributes(foreground)
        detected_attrs.extend(fg_attrs)
    if background:
        background, bg_attrs = extract_attributes(background)
        detected_attrs.extend(bg_attrs)

    foreground = foreground or 'white'
    background = background or None

    if foreground and len(foreground) < 3:
        foreground = color_map_colors(foreground)
    if background and len(background) < 3:
        background = color_map_colors(background)

    seen = set()
    detected_attrs = [a for a in detected_attrs if not (a in seen or seen.add(a))]

    return foreground.strip(), (background.strip() if background else None), detected_attrs

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

__all__ = _all_names + ['colorize', 'color_map_colors', 'getSort']

if __name__ == '__main__':
    # 1. Nama lengkap
    print(red("Error!"))
    print(bl("Im Blue"))
    print(green_on_black("Success"))

    # 2. Singkatan
    print(w_bl("White on Blue"))      # white on blue
    print(r_w("Red on White"))        # red on white
    print(g_b("Green on Black"))      # green on black
    print(lb_b("Light Blue on Black"))

    # 3. Dinamis dengan atribut
    print(colorize("Bold Red", "red-bold"))
    print(colorize("Underlined Green", fg="g", bg="b", attrs=["underline"]))

    # 4. Parsing fleksibel
    print(colorize("Blinking Magenta", "magenta-blink"))
