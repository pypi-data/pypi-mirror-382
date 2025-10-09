###############################################################################
# artpack/art_pals.py
###############################################################################
import random
from typing import List
import numpy as np
from matplotlib import colors as mcolors

# Define all palettes
pals = {
    "arctic": ["#006ACD", "#4596D7", "#8AC2E1", "#BDDFEB", "#DEEFF5", "#FFFFFF"],
    "beach": ["#E8B381", "#E7D2C1", "#7EC7F1", "#3DB0DD", "#009DEA", "#006ACD"],
    "bw": [
        "#000000",
        "#1a1a1a",
        "#333333",
        "#666666",
        "#999999",
        "#ebe1e1",
        "#ffffff",
    ],
    "brood": ["#000000", "#0A0A0A", "#141414", "#1F1F1F", "#292929", "#333333"],
    "cosmos": ["#562B91", "#5B1A61", "#BC3AA5", "#E73C88", "#4A77B5", "#1F186C"],
    "explorer": [
        "#F75231",
        "#399CFF",
        "#FFC631",
        "#7BCE52",
        "#5ACEE7",
        "#A55239",
        "#B55AA5",
        "#D6B55A",
        "#6363B5",
    ],
    "gemstones": [
        "#29295D",
        "#7C5EB8",
        "#18AFB8",
        "#005038",
        "#819126",
        "#E6C14E",
        "#A14C0C",
        "#9F232E",
    ],
    "grays": [
        "#222222",
        "#333333",
        "#444444",
        "#555555",
        "#666666",
        "#777777",
        "#888888",
        "#999999",
    ],
    "icecream": ["#FCFEFD", "#FFECA8", "#FAD8E9", "#8FD9F4", "#BF7014", "#7B4000"],
    "imagination": [
        "#DD0B80",
        "#E58E54",
        "#F1E109",
        "#A8CD35",
        "#07ADEB",
        "#572E76",
    ],
    "majestic": ["#0F061B", "#1D0B35", "#350A3C", "#471049", "#881F74"],
    "nature": ["#686C20", "#1D3A1D", "#C77F42", "#532F00", "#9C1800", "#5B0000"],
    "neon": [
        "#fc0000",
        "#fc4800",
        "#fcdb00",
        "#3ffc00",
        "#00ecfc",
        "#001dfc",
        "#6900fc",
        "#fc00f0",
        "#fc007e",
    ],
    "ocean": ["#12012E", "#144267", "#15698C", "#0695AA", "#156275"],
    "plants": ["#5ebf61", "#2f8032", "#206322", "#0c570f", "#0a380b", "#041f05"],
    "rainbow": [
        "#AF3918",
        "#A21152",
        "#822B75",
        "#612884",
        "#154BAF",
        "#0B82B9",
        "#277E9D",
        "#488E35",
        "#E3A934",
        "#f26e0a",
    ],
    "sunnyside": ["#F6BF07", "#F67C21", "#ED155A", "#F61867"],
    "super": [
        "#000000",
        "#292929",
        "#5F0E0E",
        "#363131",
        "#662E8A",
        "#B80000",
        "#C60018",
        "#005C94",
        "#E72124",
        "#4D982E",
        "#987EC1",
        "#F7C700",
    ],
}


def art_pals(
    pal: str = "ocean", n: int = 5, direction: str = "regular", randomize: bool = False
) -> List[str]:
    """
    The artpack palette picker. The `art_pals` function consists of 18 palettes.

    Parameters
    ----------
    pal : str, optional
        A character string of the desired artpack palette. Default is "ocean".

        The 18 artpack palettes include:
        - "arctic" - Icy blue and white colors
        - "beach" - Sand-colored tans and ocean-colored blue colors
        - "bw" - A gradient of black to white colors
        - "brood" - A gradient of different shades of dark gray and black colors
        - "cosmos" - Nebula-inspired blue, purple, and pink colors
        - "explorer" - Pokemon-type inspired colors
        - "gemstones" - Birthstone/Mineral-inspired colors
        - "grays" - A gradient of dark, medium, and light gray colors
        - "icecream" - A light pastel palette of cream, blue, brown, and pink colors
        - "imagination" - 90's school supply-inspired colors
        - "majestic" - Shades of majestic purple colors
        - "nature" - A mix of tan, brown, green, and red colors
        - "neon" - A neon spectrum of rainbow colors
        - "ocean" - A gradient of dark to light blue colors
        - "plants" - A gradient of dark to light green colors
        - "rainbow" - A vibrant mix of rainbow colors
        - "sunnyside" - A retro-inspired mix of pink, orange, and yellow colors
        - "super" - A marveling mix of heroic colors

    n : int, optional
        The number of colors desired in the output. Default is 5.
        Must be a positive integer with a value greater than 0.

    direction : str, optional
        The direction of the palette. Default is "regular".
        Options: "regular", "reg", "reverse", "rev"

    randomize : bool, optional
        Determines if the colors in the palette appear in a randomized order.
        Default is False.

    Returns
    -------
    list of str
        A list of hexadecimal color codes.

    Examples
    --------
    >>> colors = art_pals("rainbow", n=5)
    >>> len(colors)
    5
    """

    ###############################################################################
    # Input Checks
    ###############################################################################
    # n validation
    if not isinstance(n, int) or n <= 0:
        raise ValueError(f"n must be a positive integer. You've supplied: {n}")

    # pal validation
    if not isinstance(pal, str):
        raise TypeError(
            f"pal must be a single character string. You've supplied: {pal}"
        )

    # convert to lowercase
    pal = pal.lower()

    if pal not in pals:
        valid_pals = ", ".join(pals.keys())
        raise ValueError(
            f"'{pal}' is not a valid palette. Please choose one of the following: {valid_pals}"
        )

    # direction validation
    direction = direction.lower()
    valid_directions = ", ".join(["regular", "reg", "reverse", "rev"])
    if direction not in valid_directions:
        raise ValueError(
            f"'{direction}' is not a valid direction. `direction` must be one of: {valid_directions}"
        )

    # randomize validation
    if not isinstance(randomize, bool):
        raise TypeError("`randomize` must be True or False")

    ###############################################################################
    # Palette Generation
    ###############################################################################
    # Get base palette colors
    base_colors = pals[pal]

    # Interpolate to get n colors
    base_len = len(base_colors)
    if n <= base_len:
        # If n has fewer colors than base, just sample n
        indices = np.linspace(0, base_len - 1, n).astype(int)
        new_pal = [base_colors[i] for i in indices]
    else:
        # If n has more colors then base, interpolate
        # Convert hex to RGB
        rgb_colors = [mcolors.hex2color(c) for c in base_colors]

        # Create interpolation indices
        positions = np.linspace(0, 1, len(rgb_colors))
        new_positions = np.linspace(0, 1, n)

        # Then apply to each RGB channel
        r = np.interp(new_positions, positions, [c[0] for c in rgb_colors])
        g = np.interp(new_positions, positions, [c[1] for c in rgb_colors])
        b = np.interp(new_positions, positions, [c[2] for c in rgb_colors])

        # Convert back to hex
        new_pal = [mcolors.rgb2hex((r[i], g[i], b[i])) for i in range(n)]

    # Apply direction if applicable
    if direction in ["reverse", "rev"]:
        new_pal = new_pal[::-1]

    # Apply randomization if applicable
    if randomize:
        random.shuffle(new_pal)

    # Spit it out
    return new_pal
