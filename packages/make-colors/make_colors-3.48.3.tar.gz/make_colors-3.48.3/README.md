# 🎨 make\_colors

A simple, powerful, and cross-platform Python library for adding colors, styles, and rich markup support to your terminal output. Optimized for **Windows 10+**, Linux, and macOS.

[![Python Version](https://img.shields.io/badge/python-2.7%2B%20%7C%203.x-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📋 Table of Contents

* [✨ Features](#-features)
* [📦 Installation](#-installation)
* [🚀 Quick Start](#-quick-start)
* [🎨 Color Reference](#-color-reference)
* [💡 Usage Examples](#-usage-examples)
* [🌍 Environment Variables](#-environment-variables)
* [📚 API Reference](#-api-reference)
* [🖋 Rich Markup Support](#-rich-markup-support)
* [🖥️ Platform Support](#-platform-support)
* [🛠️ Development & Testing](#-development--testing)
* [🎯 Best Practices](#-best-practices)
* [⚠️ Error Handling](#️-error-handling)
* [📊 Performance](#-performance)
* [📑 Quick Reference](#-quick-reference)
* [🤝 Contributing](#-contributing)
* [📄 License](#-license)
* [👨‍💻 Author](#-author)

[![Example Usage](https://github.com/cumulus13/make_colors/raw/refs/heads/master/example_usage.gif)](https://github.com/cumulus13/make_colors/raw/refs/heads/master/example_usage.gif)

---

## ✨ Features

* 🖥️ **Cross-platform support** – Works on Windows, Linux, and macOS
* 🎯 **Windows 10+ optimized** – Uses native ANSI processing on Windows Console
* 🌈 **Rich color palette** – 16 standard colors with light variants
* 📝 **Simple syntax** – Full names, abbreviations, and combined formats
* 🔧 **Flexible formatting** – Foreground, background, and text attributes
* 🖋 **Rich markup** – Parse and render `[red]Error[/]` or `[bold white on red]CRITICAL[/]`
* 🚀 **Lightweight** – Zero external dependencies
* 🎛️ **Environment control** – Enable/disable colors globally with env vars
* 🛡 **Error handling** – Graceful fallbacks when unsupported colors are used

---

## 📦 Installation

```bash
pip install make_colors
```

---

## 🚀 Quick Start

```python
from make_colors import make_colors

# Simple colored text
print(make_colors("Hello World!", "red"))

# Text with background
print(make_colors("Important Message", "white", "red"))

# Using shortcuts
print(make_colors("Quick and easy", "r", "bl"))  # red text, blue background

# Using underscore notation
print(make_colors("One-liner style", "green_yellow"))  # green text on yellow background

# Rich markup
print(make_colors("[bold white on red] CRITICAL [/]") )

# import all 
from make_colors import *

print(bl("Im Blue"))
color = Colors('red', 'white')
print(color("White on Red"))
color = Color('white', 'red')
print(color("TEST"))

```

---

## 🎨 Color Reference

### Available Colors

| Color Name | Shortcuts     | Light Variant | Light Shortcut |
| ---------- | ------------- | ------------- | -------------- |
| black      | b, bk         | lightblack    | lb             |
| red        | r, rd, re     | lightred      | lr             |
| green      | g, gr, ge     | lightgreen    | lg             |
| yellow     | y, ye, yl     | lightyellow   | ly             |
| blue       | bl            | lightblue     | lb             |
| magenta    | m, mg, ma     | lightmagenta  | lm             |
| cyan       | c, cy, cn     | lightcyan     | lc             |
| white      | w, wh, wi, wt | lightwhite    | lw             |

### Color Preview

```python
# Standard colors
print(make_colors("■ Black text", "black"))
print(make_colors("■ Red text", "red"))
print(make_colors("■ Green text", "green"))
print(make_colors("■ Yellow text", "yellow"))
print(make_colors("■ Blue text", "blue"))
print(make_colors("■ Magenta text", "magenta"))
print(make_colors("■ Cyan text", "cyan"))
print(make_colors("■ White text", "white"))

# Light variants
print(make_colors("■ Light Red", "lightred"))
print(make_colors("■ Light Green", "lightgreen"))
print(make_colors("■ Light Blue", "lightblue"))
print(make_colors("■ Light Yellow", "lightyellow"))
```

---

## 💡 Usage Examples

### Basic Usage

```python
print(make_colors("Full color names", "red", "white"))
print(make_colors("Using shortcuts", "r", "w"))
print(make_colors("Mixed notation", "red", "w"))
```

### Separator Notation

```python
# Using underscore separator
print(make_colors("Error occurred!", "red_white"))
print(make_colors("Success!", "green_black"))
print(make_colors("Warning!", "yellow_red"))

# Using dash separator
print(make_colors("Info message", "blue-white"))
print(make_colors("Debug info", "cyan-black"))

# Using comma separator
print(make_colors("Critical message", "white,blue"))
print(make_colors("Alert info", "w,r"))

```

### Advanced Examples

```python
# System status display
def show_status(service, status):
    if status == "running":
        return make_colors(f"[✓] {service}", "lightgreen", "black")
    elif status == "stopped":
        return make_colors(f"[✗] {service}", "lightred", "black")
    else:
        return make_colors(f"[?] {service}", "lightyellow", "black")

print(show_status("Web Server", "running"))
print(show_status("Database", "stopped"))
print(show_status("Cache", "unknown"))

# Log level formatting
def log_message(level, message):
    colors = {
        "ERROR": ("lightwhite", "red"),
        "WARNING": ("black", "yellow"),
        "INFO": ("lightblue", "black"),
        "DEBUG": ("lightgrey", "black")
    }
    
    fg, bg = colors.get(level, ("white", "black"))
    return f"{make_colors(f' {level} ', fg, bg)} {message}"

print(log_message("ERROR", "Connection failed"))
print(log_message("WARNING", "Deprecated method used"))
print(log_message("INFO", "Server started successfully"))
print(log_message("DEBUG", "Variable value: 42"))
```

### Attributes

```python
print(make_colors("Bold text", "red", attrs=["bold"]))
print(make_colors("Underlined", "blue", attrs=["underline"]))
print(make_colors("Italic + Bold", "green", attrs=["italic", "bold"]))
```

### Progress Bar Indicators

```python
import time
for i in range(0, 101, 20):
    bar = "█" * (i // 5) + "░" * (20 - i // 5)
    print(f"\r{make_colors(f'[{bar}] {i}%', 'yellow')}", end="")
    time.sleep(0.2)
print()

def progress_bar(current, total, width=50):
    percentage = current / total
    filled = int(width * percentage)
    bar = "█" * filled + "░" * (width - filled)
    
    if percentage < 0.5:
        color = "red"
    elif percentage < 0.8:
        color = "yellow"
    else:
        color = "green"
    
    return make_colors(f"[{bar}] {current}/{total} ({percentage:.1%})", color)

# Simulate progress
for i in range(0, 101, 10):
    print(f"\r{progress_bar(i, 100)}", end="", flush=True)
    time.sleep(0.1)
print()  # New line after completion
```

### Menu Systems

```python
def create_menu():
    options = [
        ("1", "Start Application", "green"),
        ("2", "Settings", "yellow"),
        ("3", "Help", "blue"),
        ("4", "Exit", "red")
    ]
    
    print(make_colors(" 🎯 Main Menu ", "white", "blue"))
    print()
    
    for key, option, color in options:
        print(f"  {make_colors(key, 'white', color)} {option}")
    
    print()
    return input("Select option: ")

# Usage
choice = create_menu()
```

---

## 🌍 Environment Variables

| Variable            | Values              | Description                        |
| ------------------- | ------------------- | ---------------------------------- |
| `MAKE_COLORS`       | `0` or `1`          | Disable/enable colors globally     |
| `MAKE_COLORS_FORCE` | `0`, `1`, `True`    | Force colors even when unsupported |
| `MAKE_COLORS_DEBUG` | `1`, `true`, `True` | Enable debug parsing logs          |

Example:

```python
import os

# Disable colors
os.environ['MAKE_COLORS'] = '0'
print(make_colors("No colors", "red"))  # Output: "No colors" (no coloring)

# Force colors (useful for CI/CD or redirected output)
os.environ['MAKE_COLORS_FORCE'] = '1'
print(make_colors("Forced colors", "green"))  # Always colored
```

---

## 📚 API Reference

### `make_colors(string, foreground='white', background=None, attrs=[], force=False)`

Main function to colorize strings with ANSI or Rich markup.

* `string` *(str)* – Input text, supports Rich markup like `[red]Error[/]`
* `foreground` *(str)* – Foreground color
* `background` *(str|None)* – Background color
* `attrs` *(list)* – List of attributes: `bold`, `underline`, `italic`, etc.
* `force` *(bool)* – Force enable colors

**Returns:**
- `str` (Colorized string with ANSI string escape codes)

---

### `make_color(...)`

Alias for `make_colors`.

### `print(string, ...)`

Convenience print wrapper that applies `make_colors` before printing.

### `parse_rich_markup(text)`

Parses strings like `[bold red on black]Hello[/]` into `(content, fg, bg, style)` tuples. Supports multiple tags.

### `getSort(data, foreground, background)`

Parses combined formats like `red-yellow`, `g_b`, expanding into `(fg, bg)`.

### `color_map(code)`

Maps abbreviations like `r`, `bl`, `lg` to full names.

**Examples:**
```python
# Basic usage
make_colors("Hello", "red")

# With background
make_colors("Hello", "white", "red")

# Using shortcuts
make_colors("Hello", "w", "r")

# Separator notation
make_colors("Hello", "white_red")

# Force colors
make_colors("Hello", "red", force=True)
```

### `MakeColors` class

* `colored(string, fg, bg, attrs)` → low-level ANSI output
* `rich_colored(string, color, bg, style)` → Rich style support
* `supports_color()` → Detect terminal support, return: `bool`: True if colors are supported, False otherwise

```python
from make_colors import MakeColors

if MakeColors.supports_color():
    print("Colors are supported!")
else:
    print("Colors not supported on this terminal")
```

### Exceptions

* `MakeColorsError` – Raised when invalid colors are used
* `MakeColorsWarning` – Non-critical fallback warnings

---

## 🖋 Rich Markup Support

The library supports **Rich-style markup** similar to the `rich` package:

```python
print(make_colors("[red]Error[/] [bold white on blue]CRITICAL[/] [green]OK[/]"))
```

Supported styles:

* **bold**, **italic**, **underline**, **dim**, **blink**, **reverse**, **strikethrough**

---

## 🖥️ Platform Support


### Windows
* **Windows 10+**       ✅ (full ANSI support)
* **Older Windows**     ⚠️ requires ANSICON
* **Windows Terminal**: 👍 Excellent support with all features

### Linux/Unix
* **Most terminals**: ✅ Full support (xterm, gnome-terminal, konsole, etc.), almost all terminals supported
* **Tmux/Screen**:    ✅ Supported
* **SSH sessions**:   ✅ Supported when terminal supports colors

### macOS
- **Terminal.app**:    ✅ Full support
- **iTerm2**:          ✅ Excellent support
- **Other terminals**: ✅  Generally well supported
---

## 🛠️ Development & Testing

### Testing Colors

```python
def test_all_colors():
    """Test all available colors"""
    colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    light_colors = [f'light{color}' for color in colors if color != 'black'] + ['lightgrey']
    
    print("=== Standard Colors ===")
    for color in colors:
        print(make_colors(f"  {color.ljust(10)}", color, "black"))
    
    print("\n=== Light Colors ===")
    for color in light_colors:
        print(make_colors(f"  {color.ljust(15)}", color, "black"))

# Run the test
test_all_colors()
```

### Check Support

```python
from make_colors import MakeColors
print("Supports colors:", MakeColors.supports_color())
```

```python
def test_all_colors():
    """Test all available colors"""
    colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    light_colors = [f'light{color}' for color in colors if color != 'black'] + ['lightgrey']
    
    print("=== Standard Colors ===")
    for color in colors:
        print(make_colors(f"  {color.ljust(10)}", color, "black"))
    
    print("\n=== Light Colors ===")
    for color in light_colors:
        print(make_colors(f"  {color.ljust(15)}", color, "black"))

# Run the test
test_all_colors()

---

## 🎯 Best Practices

1. **Always check color support** `MakeColors.supports_color()` before production use
2. **Provide fallbacks** for environments without color support (e.g. plain text when disabled)
3. **Use env vars for CI/CD or logging**
4. **Choose contrasting colors** for better readability
5. **Test on multiple OSes/terminals/platforms** to ensure compatibility

```python
from make_colors import make_colors, MakeColors

def safe_print(text, fg="white", bg=None):
    """Safely print colored text with fallback"""
    if MakeColors.supports_color():
        print(make_colors(text, fg, bg))
    else:
        print(f"[{fg.upper()}] {text}")

# Usage
safe_print("This works everywhere!", "green")
```

## 🧙 Magick
```python
    
    from make_colors import *

    print(red("Error!"))
    print(bl("Im Blue"))
    print(green_on_black("Success"))

    # Abbreviation
    print(w_bl("White on Blue"))      # white on blue
    print(r_w("Red on White"))        # red on white
    print(g_b("Green on Black"))      # green on black
    print(lb_b("Light Blue on Black"))

    color = Colors('red', 'white')
    print(color("White on Red"))
    color = Color('white', 'red')
    print(color("TEST"))


    # Try and see what happened 👏 😄
```

---

## ⚠️ Error Handling

* Invalid color → falls back to white on black
* Unknown attribute → ignored silently
* Raise `MakeColorsError` for invalid color names (if strict)
* Raise `MakeColorsWarning` for warnings

```python
try:
    print(make_colors("Oops", "notacolor"))
except Exception as e:
    print("Handled:", e)
```

---

## 📊 Performance

* Traditional call: \~0.00001s per render
* Rich markup parsing: slightly slower (\~+10–15%)
* Suitable for **high-frequency logging**

---

## 📑 Quick Reference

* ✅ Single color: `[red]text[/]`
* ✅ With background: `[white on red]text[/]`
* ✅ With style: `[bold green]text[/]`
* ✅ Combined: `[bold white on red]ALERT[/]`
* ✅ Multiple tags: `[cyan]Info[/] [red]Error[/]`

---

## 🤝 Contributing

PRs welcome! Open issues for feature requests or bugs.
Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

Licensed under the **MIT License**. See [LICENSE](LICENSE).

---

## 👨‍💻 Author

**Hadi Cahyadi**
📧 [cumulus13@gmail.com](mailto:cumulus13@gmail.com)

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)

[Support me on Patreon](https://www.patreon.com/cumulus13)

---

✨ Made with ❤️ by Hadi Cahyadi for colorful terminal experiences!
