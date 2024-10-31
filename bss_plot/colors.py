import json
import os
import re

import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import yaml
from pybtex.database import Entry
from matplotlib.colors import rgb2hex


class Palette:
    def __init__(self, colors=None, reference=None, **kwargs):
        """
        Initialize the palette with an optional dictionary of colors.

        Parameters:
            colors (dict): Optional dictionary of colors where each key is a color name,
                           and each value is either a HEX string or an RGB tuple.
        """
        self.colors = {}

        if "name" in kwargs:
            self.name = kwargs.pop("name")
        else:
            self.name = "Custom Palette"

        if colors is not None:

            if isinstance(colors, dict):
                for name, color in colors.items():
                    if isinstance(color, tuple) and len(color) == 3:
                        self.add_color(name, rgb=color)
                    elif isinstance(color, str) and color.startswith("#"):
                        self.add_color(name, hex_code=color)
                    else:
                        raise ValueError(
                            "Colors must be in RGB tuple or HEX string format."
                        )
            else:
                for color in colors:
                    if len(color) == 3:
                        self.add_color(f"color_{len(self.colors) + 1}", rgb=color)
                    elif isinstance(color, str) and color.startswith("#"):
                        self.add_color(f"color_{len(self.colors) + 1}", hex_code=color)
                    else:
                        raise ValueError(
                            "Colors must be in RGB tuple or HEX string format."
                        )

        if reference:
            self.reference = reference

    # def __repr__(self):
    #     self.get_cmap()

    def add_color(self, name, rgb=None, hex_code=None):
        """
        Add a color to the palette.

        Parameters:
            name (str): Name of the color.
            rgb (tuple): RGB tuple (R, G, B) with values from 0 to 255.
            hex_code (str): HEX color code as a string (e.g., '#FF5733').
        """
        if rgb is not None:
            if max(rgb) > 1:
                rgb = tuple(value / 255 for value in rgb)
            hex_color = rgb2hex(rgb)
        elif hex_code is not None:
            hex_color = hex_code
            rgb = tuple(int(hex_code[i : i + 2], 16) for i in (1, 3, 5))
        else:
            raise ValueError("Either rgb or hex_code must be provided.")

        self.colors[name] = {"rgb": rgb, "hex": hex_color}

    def get_color(self, name):
        """
        Retrieve a color from the palette by name.

        Parameters:
            name (str): Name of the color.

        Returns:
            dict: A dictionary with RGB and HEX values of the color.
        """
        return self.colors.get(name, None)

    def get_hex_colors(self):
        """
        Get a list of all colors in HEX format.

        Returns:
            list: List of HEX color codes as strings.
        """
        return [color["hex"] for color in self.colors.values()]

    def get_rgb_colors(self):
        """
        Get a list of all colors in RGB format.

        Returns:
            list: List of RGB color tuples.
        """
        return [color["rgb"] for color in self.colors.values()]

    def to_json(self, file_path=None):
        """
        Export the palette as JSON.

        Parameters:
            file_path (str): Optional path to save the JSON file.

        Returns:
            str: JSON string if file_path is None, otherwise saves JSON to file.
        """
        if file_path:
            with open(file_path, "w") as f:
                json.dump(self.colors, f, indent=4)
        return json.dumps(self.colors, indent=4)

    def to_yaml(self, file_path=None):
        """
        Export the palette as YAML.

        Parameters:
            file_path (str): Optional path to save the YAML file.

        Returns:
            str: YAML string if file_path is None, otherwise saves YAML to file.
        """
        if file_path:
            with open(file_path, "w") as f:
                yaml.dump(self.colors, f)
        return yaml.dump(self.colors)

    def to_css(self, file_path=None):
        """
        Export the palette as a CSS custom properties file.

        Parameters:
            file_path (str): Optional path to save the CSS file.

        Returns:
            str: CSS string if file_path is None, otherwise saves CSS to file.
        """
        css = ":root {\n"
        for name, color in self.colors.items():
            css += f"  --{name.lower().replace(' ', '-')}: {color['hex']};\n"
        css += "}"

        if file_path:
            with open(file_path, "w") as f:
                f.write(css)
        return css

    def plot(self):
        """
        Display a bar plot of the colors in the palette.
        """
        hex_colors = self.get_hex_colors()
        color_names = list(self.colors.keys())

        fig, ax = plt.subplots(figsize=(len(hex_colors), 1))
        ax.imshow([hex_colors], aspect="auto", extent=[0, len(hex_colors), 0, 1])
        ax.set_yticks([])

        # Add color labels below each color bar
        ax.set_xticks(range(len(hex_colors)))
        ax.set_xticklabels(color_names, rotation=45, ha="right")

        plt.tight_layout()
        plt.show()

    def update_rc_params(self):
        """
        Update matplotlib's rcParams using the palette colors.
        Sets the color cycle and other relevant properties.
        """
        hex_colors = self.get_hex_colors()

        # Update color cycle and other rcParams with available colors
        mpl.rcParams["axes.prop_cycle"] = mpl.cycler("color", hex_colors)

    def create_sequential_colormaps(self, base_color="#FFFFFF"):
        """
        Create sequential colormaps from white to each color in the palette.

        Returns:
            dict: A dictionary where keys are color names and values are
                LinearSegmentedColormap instances transitioning from white
                to the respective color.
        """
        colormaps = {}

        for name, color in self.colors.items():
            # Create a colormap that transitions from white to the color
            cmap = mcolors.LinearSegmentedColormap.from_list(
                f"{name}_sequential", [base_color, color["hex"]]
            )
            colormaps[name] = cmap

        return colormaps

    def create_colormap(self, type="linear"):
        """
        Create a colormap from the palette colors.

        Returns:
            LinearSegmentedColormap: A colormap transitioning between the colors in the palette.
        """

        # Create a colormap that transitions between the colors in the palette
        colors = [color["hex"] for color in self.colors.values()]
        if type == "linear":
            cmap = mcolors.LinearSegmentedColormap.from_list("custom", colors)
        if type == 'listed':
            cmap = mcolors.ListedColormap(colors)
        cmap.name = self.name
        return cmap

    def get_cmap(self, type='linear'):
        return self.create_colormap(type=type)


colorblind_palette = Palette(
    {
        "Black": (0, 0, 0),
        "Orange": (230, 159, 0),
        "Sky Blue": (86, 180, 233),
        "Bluish Green": (0, 158, 115),
        "Yellow": (240, 228, 66),
        "Blue": (0, 114, 178),
        "Vermillion": (213, 94, 0),
        "Reddish Purple": (204, 121, 167),
    },
    reference=Entry(
        "article",
        fields={
            "title": "Points of view: Color blindness",
            "journal": "Nature Methods",
            "volume": "8",
            "pages": "441",
            "year": "2011",
            "doi": "10.1038/nmeth.1618",
        },
        persons={"author": [("Wong", "B.")]},
    ),
)

ggsci_palette = Palette(
    {
        "Red": "#E64B35B2",
        "Blue": "#4DBBD5B2",
        "Green": "#00A087B2",
        "Dark Blue": "#3C5488B2",
        "Peach": "#F39B7FB2",
        "Lavender": "#8491B4B2",
        "Teal": "#91D1C2B2",
        "Crimson": "#DC0000B2",
        "Brown": "#7E6148B2",
    },
    reference=Entry(
        "manual",
        fields={
            "title": "ggsci: Scientific Journal and Sci-Fi Themed Color Palettes for 'ggplot2'",
            "author": "Nan Xiao",
            "year": "2018",
            "url": "https://CRAN.R-project.org/package=ggsci",
        },
    ),
)


class ColorLoader:
    def __init__(
        self, base_path=os.path.join(os.path.dirname(__file__), "scientific_color_maps")
    ):
        """
        Initialize the ColorLoader with the base path where color maps are stored.

        Parameters:
            base_path (str): Root directory containing the color map folders.
        """
        self.base_path = base_path

        self.reference = Entry(
            "article",
            fields={
                "title": "The misuse of colour in science communication",
                "journal": "Nature Communications",
                "volume": "11",
                "pages": "5444",
                "year": "2020",
                "doi": "10.1038/s41467-020-19160-7",
            },
            persons={
                "author": [("Crameri", "F."), ("Shephard", "G.E."), ("Heron", "P.J.")]
            },
        )

        self.palettes = self._load_palettes()

    def _load_palettes(self):
        """
        Load all palettes from the directory structure into Palette instances.

        Returns:
            dict: A dictionary of palettes where keys are palette names and values are Palette instances.
        """
        palettes_by_type = {}
        for cmaptype in ["sequential", "diverging", "multisequential", "cyclic"]:
            palettes = {}
            for file in os.listdir(os.path.join(self.base_path, cmaptype)):
                if file.endswith(".txt") and not re.search(r"(10|25|50|HEX)", file):
                    palette_name = os.path.basename(file).split(".")[0]
                    colors = self._load_colors_from_file(
                        os.path.join(self.base_path, cmaptype, file)
                    )
                    if palette_name not in palettes:
                        palettes[palette_name] = Palette(
                            colors=colors, reference=self.reference, name=palette_name
                        )
            palettes_by_type[cmaptype] = dict(sorted(palettes.items()))
        return palettes_by_type

    def _load_colors_from_file(self, file_path):
        """
        Load colors from a file with RGB values (0-1 range) and convert them to HEX format.

        Parameters:
            file_path (str): Path to the color map file.

        Returns:
            dict: Dictionary of color names and their HEX values.
        """
        colors = {}
        with open(file_path, "r") as f:
            for idx, line in enumerate(f):
                parts = line.strip().split()
                if len(parts) == 3:  # RGB values
                    try:
                        rgb = tuple(float(value) for value in parts)
                        hex_code = "#{:02x}{:02x}{:02x}".format(
                            int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
                        )
                        color_name = f"color_{idx + 1}"  # Generate unique color names
                        colors[color_name] = hex_code
                    except ValueError:
                        raise ValueError(
                            f"Invalid RGB format in {file_path} on line {idx + 1}: {line}"
                        )
        return colors

    def get_palette(
        self,
        name,
        maptype="sequential",
    ):
        """
        Retrieve a Palette instance by name.

        Parameters:
            name (str): Name of the palette.

        Returns:
            Palette: A Palette instance if found, else None.
        """
        return self.palettes[maptype].get(name)
