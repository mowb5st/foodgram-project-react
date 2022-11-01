import webcolors


def color_to_hex(color):
    # hex_value_css = webcolors.CSS3_NAMES_TO_HEX(color)
    hex_value = webcolors.name_to_hex(color)
    print('input:', color, '|', 'output:', hex_value)


def hex_to_color(hex):
    color = webcolors.hex_to_name(hex)
    print('input:', hex, '|', 'output:', color)


color_to_hex('red')
hex_to_color('#ff0000')
