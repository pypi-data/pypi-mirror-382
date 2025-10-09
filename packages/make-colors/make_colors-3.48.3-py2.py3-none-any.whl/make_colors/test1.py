from make_colors import make_colors

print(make_colors("TEST", 'lw', 'lr') + " --> " + make_colors("TEST 2", 'lw', 'm'))
print(make_colors("TEST1", 'lw', 'bl') + " --> " + make_colors("TEST 2", 'lw', 'm'))

print(make_colors("WHITE on RED ", 'white_red'))
print(make_colors("WHITE on RED ", 'white-red'))
print(make_colors("WHITE on RED shortcut", 'w_r'))

print(make_colors("TEST", 'lw', 'r'))