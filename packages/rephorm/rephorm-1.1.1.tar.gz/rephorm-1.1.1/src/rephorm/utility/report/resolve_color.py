from rephorm.dict.colors import color_codes


def resolve_color(color):

    normalized_color = color.lower()

    # Check if the input is within color_codes dict and if so - return hex code
    if normalized_color in color_codes:
        return color_codes[normalized_color]

    # Hex validation
    if normalized_color.startswith('#') and len(normalized_color) == 7:
        try:
            # raise a ValueError if not a valid hex
            int(normalized_color[1:], 16)
            return normalized_color
        except ValueError:
            pass

    return color

# This function is used to resolve the highlight color for chart
# When it comes in natural language such as "green", it resolves
# based on our set of colors.
# In color_codes the value must be in hex, cannot be in RGB.
def resolve_highlight_color(color, alpha=1):
    if color.lower().startswith(("#", "hsl", "rgb", "hsla", "rgba")):
        return color
    hex = resolve_color(color)
    return hex_to_rgba(hex, alpha=alpha)

def hex_to_rgba(hex_color, alpha=1):

    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"