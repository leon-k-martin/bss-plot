import string


def get_alphabet(index, uppercase=False):
    """
    Get the alphabet letter(s) corresponding to an index (1-based).
    Extends beyond 'Z' to 'AA', 'AB', etc., if needed.

    Parameters:
        index (int): The 1-based index (1 = A, 2 = B, ..., 27 = AA).
        uppercase (bool): If True, returns uppercase letters; otherwise, lowercase.

    Returns:
        str: The corresponding letter(s).
    """
    alphabet = string.ascii_uppercase if uppercase else string.ascii_lowercase
    result = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = alphabet[remainder] + result
    return result


def add_panel_number(
    ax,
    label,
    option="letters",
    background=True,
    loc="upper left",
    text_kwargs={
        "fontsize": 16,
        "fontweight": "bold",
        "va": "top",
    },
):
    """
    Adds a label to the given axis in the upper left corner. If option is 'letters'
    and the label is a number, it converts it to the corresponding alphabetical letter(s).

    Parameters:
        ax (matplotlib.axes.Axes): The axis to add the label to.
        label (int or str): The label to place in the upper left corner.
        option (str): 'letters' to convert numbers to letters, 'numbers' to use label as-is.
    """
    if option == "letters" and isinstance(label, int):
        label = get_alphabet(label)

    if loc == "upper left":
        text_kwargs['ha'] = 'left'
        x = 0.05
        y = 1
    elif loc == "upper right":
        text_kwargs['ha'] = 'right'
        x = 0.95
        y = 1

    if background:
        text_kwargs["bbox"] = {
            "boxstyle": "round,pad=0.1",
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.8,
        }

    ax.text(
        x,
        y,
        str(label),
        transform=ax.transAxes,  # Relative to the axis
        **text_kwargs,
    )
