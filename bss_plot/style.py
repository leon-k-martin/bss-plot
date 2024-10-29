import matplotlib.pyplot as plt
import os
import bss_plot  # Import your package to access its path


def use_style(style="bss"):
    # Define the path to the custom style
    style_path = os.path.join(
        os.path.dirname(bss_plot.__file__), "styles", f"{style}.mplstyle"
    )
    if not os.path.exists(style_path):
        raise ValueError(
            f"Style '{style}' not found in the package. Available styles: {os.listdir(style_path)}"
        )
    plt.style.use(style_path)  # Load the custom style from the package
