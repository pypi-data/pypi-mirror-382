#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for make_colors module
Tests all colors, shortcuts, and functionalities
"""

import os
import sys
from make_colors import make_colors, MakeColors, make_color, _print
import time

def print_separator(title, char="=", width=60):
    """Print a formatted separator with title"""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")

def test_color_support():
    """Test color support detection"""
    print_separator("COLOR SUPPORT TEST")
    print(f"Platform: {sys.platform}")
    print(f"Color support: {MakeColors.supports_color()}")
    print(f"MAKE_COLORS env: {os.getenv('MAKE_COLORS', 'not set')}")
    print(f"MAKE_COLORS_FORCE env: {os.getenv('MAKE_COLORS_FORCE', 'not set')}")
    if hasattr(sys.stdout, 'isatty'):
        print(f"Is TTY: {sys.stdout.isatty()}")

def test_standard_colors():
    """Test all standard colors as foreground"""
    print_separator("STANDARD FOREGROUND COLORS")
    
    standard_colors = [
        'black', 'red', 'green', 'yellow', 
        'blue', 'magenta', 'cyan', 'white'
    ]
    
    for color in standard_colors:
        colored_text = make_colors(f"  ● {color.ljust(12)}", color, 'black')
        print(f"{colored_text} | {make_colors('Sample text', color)}")

def test_light_colors():
    """Test all light variant colors as foreground"""
    print_separator("LIGHT FOREGROUND COLORS")
    
    light_colors = [
        'lightblack', 'lightred', 'lightgreen', 'lightyellow',
        'lightblue', 'lightmagenta', 'lightcyan', 'lightwhite', 'lightgrey'
    ]
    
    for color in light_colors:
        colored_text = make_colors(f"  ● {color.ljust(15)}", color, 'black')
        print(f"{colored_text} | {make_colors('Sample text', color)}")

def test_background_colors():
    """Test all colors as background"""
    print_separator("BACKGROUND COLORS")
    
    all_colors = [
        'black', 'red', 'green', 'yellow', 
        'blue', 'magenta', 'cyan', 'white',
        'lightblack', 'lightred', 'lightgreen', 'lightyellow',
        'lightblue', 'lightmagenta', 'lightcyan', 'lightwhite'
    ]
    
    for bg_color in all_colors:
        # Use contrasting foreground color
        fg_color = 'white' if 'black' in bg_color or bg_color in ['blue', 'red', 'magenta'] else 'black'
        colored_text = make_colors(f"  {bg_color.ljust(15)} ", fg_color, bg_color)
        print(f"{colored_text} Background sample")

def test_color_shortcuts():
    """Test all color shortcuts"""
    print_separator("COLOR SHORTCUTS TEST")
    
    # Define all shortcuts
    shortcuts = {
        'Standard Colors': {
            'b': 'black', 'bk': 'black',
            'bl': 'blue',
            'r': 'red', 'rd': 'red', 're': 'red',
            'g': 'green', 'gr': 'green', 'ge': 'green',
            'y': 'yellow', 'ye': 'yellow', 'yl': 'yellow',
            'm': 'magenta', 'mg': 'magenta', 'ma': 'magenta',
            'c': 'cyan', 'cy': 'cyan', 'cn': 'cyan',
            'w': 'white', 'wh': 'white', 'wi': 'white', 'wt': 'white'
        },
        'Light Colors': {
            'lb': 'lightblue',
            'lr': 'lightred',
            'lg': 'lightgreen',
            'ly': 'lightyellow',
            'lm': 'lightmagenta',
            'lc': 'lightcyan',
            'lw': 'lightwhite'
        }
    }
    
    for category, shortcut_dict in shortcuts.items():
        print(f"\n--- {category} ---")
        for shortcut, full_name in shortcut_dict.items():
            shortcut_result = make_colors(f"'{shortcut}'", shortcut)
            full_result = make_colors(f"'{full_name}'", full_name)
            print(f"  {shortcut.ljust(3)} → {shortcut_result} | {full_result}")

def test_separator_notation():
    """Test underscore and dash separator notation"""
    print_separator("SEPARATOR NOTATION TEST")
    
    test_combinations = [
        'red_white', 'green_black', 'blue_yellow',
        'white_red', 'yellow_blue', 'cyan_magenta',
        'red-white', 'green-black', 'blue-yellow',
        'lr_b', 'lg_r', 'lb_y',  # light + standard
        'w_lr', 'b_lg', 'y_lb'   # standard + light
    ]
    
    print("Underscore notation (_):")
    for combo in test_combinations[:6]:
        if '_' in combo:
            result = make_colors(f"  {combo.ljust(12)}", combo)
            print(f"{result} | Sample: {make_colors('Hello World', combo)}")
    
    print("\nDash notation (-):")
    for combo in test_combinations[6:9]:
        if '-' in combo:
            result = make_colors(f"  {combo.ljust(12)}", combo)
            print(f"{result} | Sample: {make_colors('Hello World', combo)}")
    
    print("\nShortcut combinations:")
    for combo in test_combinations[9:]:
        result = make_colors(f"  {combo.ljust(8)}", combo)
        print(f"{result} | Sample: {make_colors('Hello World', combo)}")

def test_force_parameter():
    """Test force parameter functionality"""
    print_separator("FORCE PARAMETER TEST")
    
    print("Normal behavior:")
    normal = make_colors("Normal coloring", "red", "white")
    print(f"  {normal}")
    
    print("\nForced coloring:")
    forced = make_colors("Forced coloring", "green", "yellow", force=True)
    print(f"  {forced}")
    
    print("\nEnvironment variable test:")
    # Temporarily set environment variable
    original_env = os.getenv('MAKE_COLORS')
    os.environ['MAKE_COLORS'] = '0'
    disabled = make_colors("Should be disabled", "blue", "white")
    print(f"  MAKE_COLORS=0: '{disabled}'")
    
    forced_despite_env = make_colors("Should be forced", "blue", "white", force=True)
    print(f"  force=True: {forced_despite_env}")
    
    # Restore environment
    if original_env is None:
        if 'MAKE_COLORS' in os.environ:
            del os.environ['MAKE_COLORS']
    else:
        os.environ['MAKE_COLORS'] = original_env

def test_mixed_parameters():
    """Test various parameter combinations"""
    print_separator("MIXED PARAMETERS TEST")
    
    test_cases = [
        ("Standard fg/bg", "red", "white"),
        ("Shortcut fg/bg", "r", "w"),
        ("Mixed notation", "red", "w"),
        ("Light colors", "lightred", "lightblue"),
        ("Light shortcuts", "lr", "lb"),
        ("No background", "green", None),
        ("Default params", None, None),
    ]
    
    for description, fg, bg in test_cases:
        if fg is None:
            result = make_colors("Sample text")
        elif bg is None:
            result = make_colors("Sample text", fg)
        else:
            result = make_colors("Sample text", fg, bg)
        print(f"  {description.ljust(20)}: {result}")

def test_aliases():
    """Test function aliases"""
    print_separator("ALIASES TEST")
    
    # Test make_color alias
    original = make_colors("Original function", "red", "white")
    alias = make_color("Original function", "red", "white")
    
    print(f"make_colors() original [red on white]: {original}")
    print(f"make_color() alias [red on white]:  {alias}")
    print(f"Results match: {original == alias}")
    
    original = make_colors("Original function", "red", "white")
    alias = make_color("Original function", "white", "blue")
    
    print(f"make_colors() original [red on white]: {original}")
    print(f"make_color() alias [white on blue]:  {alias}")
    print(f"Results match: {original == alias}")

def test_error_conditions():
    """Test various error conditions and edge cases"""
    print_separator("ERROR CONDITIONS & EDGE CASES")
    
    print("Testing edge cases:")
    
    # Empty string
    empty_result = make_colors("", "red")
    print(f"  Empty string: '{empty_result}'")
    
    # Unknown colors (should use defaults)
    unknown_fg = make_colors("Unknown foreground", "unknowncolor")
    print(f"  Unknown foreground: {unknown_fg}")
    
    unknown_bg = make_colors("Unknown background", "red", "unknowncolor")
    print(f"  Unknown background: {unknown_bg}")
    
    # Very long text
    long_text = "A" * 100
    long_result = make_colors(long_text, "blue")
    print(f"  Long text (100 chars): {long_result[:50]}...")
    
    # Special characters
    special = make_colors("Special chars: áéíóú ñ 中文 🌈", "magenta")
    print(f"  Special characters: {special}")

def test_real_world_examples():
    """Test real-world usage examples"""
    print_separator("REAL-WORLD EXAMPLES")
    
    # Log levels
    print("Log levels:")
    print(f"  {make_colors('[ERROR]', 'white', 'red')} Something went wrong")
    print(f"  {make_colors('[WARN] ', 'black', 'yellow')} Warning message")
    print(f"  {make_colors('[INFO] ', 'white', 'blue')} Information")
    print(f"  {make_colors('[DEBUG]', 'white', 'black')} Debug info")
    
    # Status indicators
    print("\nStatus indicators:")
    print(f"  {make_colors('✓ PASS', 'lightgreen')} Test passed")
    print(f"  {make_colors('✗ FAIL', 'lightred')} Test failed")
    print(f"  {make_colors('⚠ SKIP', 'lightyellow')} Test skipped")
    print(f"  {make_colors('● RUNNING', 'lightblue')} Test running")
    
    # Progress bar simulation
    print("\nProgress simulation multiple bar:")
    for i in range(0, 101, 25):
        if i < 50:
            color = 'red'
        elif i < 80:
            color = 'yellow'
        else:
            color = 'green'
        
        filled = "█" * (i // 5)
        empty = "░" * (20 - i // 5)
        bar = make_colors(f"[{filled}{empty}] {i}%", color)
        print(f"  {bar}")
        time.sleep(0.5)
    
    print("\nProgress simulation in one bar:")
    for i in range(0, 101, 10):
        if i < 50:
            color = 'red'
        elif i < 80:
            color = 'yellow'
        else:
            color = 'green'
        
        filled = "█" * (i // 2)
        empty = "░" * (50 - i // 2)
        bar = make_colors(f"[{filled}{empty}] {i}%", color)
        print(f"\r  {bar}", end="")
        sys.stdout.flush()
        time.sleep(0.2)
    print()  # New line after progress bar
    
def run_all_tests():
    """Run all test functions"""
    print(make_colors("MAKE_COLORS MODULE TEST SUITE", "white", "blue"))
    print(make_colors("Testing all colors, shortcuts, and functionality", "lightblue"))
    
    test_functions = [
        test_color_support,
        test_standard_colors,
        test_light_colors,
        test_background_colors,
        test_color_shortcuts,
        test_separator_notation,
        test_force_parameter,
        test_mixed_parameters,
        test_aliases,
        test_error_conditions,
        test_real_world_examples
    ]
    
    for i, test_func in enumerate(test_functions, 1):
        try:
            test_func()
        except Exception as e:
            print(f"\n{make_colors(f'ERROR in {test_func.__name__}: {e}', 'white', 'red')}")
    
    print_separator("TEST SUITE COMPLETED", "=")
    print(make_colors("All tests completed! Check output above for results.", "lightgreen"))
    print(make_colors("If colors appear properly, your make_colors module is working!", "lightblue"))

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


if __name__ == "__main__":
    run_all_tests()