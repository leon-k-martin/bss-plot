import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from matplotlib import colormaps
from matplotlib.colors import Normalize


def find_optimal_slice(streamlines, affine, plane="coronal"):
    """
    Find the optimal slice position for visualizing streamlines on a 2D plane.

    Parameters:
    streamlines (list of ndarray): List of streamlines, where each streamline is an ndarray of shape (n_points, 3).
    affine (ndarray): Affine transformation matrix for converting voxel coordinates to real-world coordinates.
    plane (str, optional): The plane to plot ("sagittal", "coronal", "horizontal").

    Returns:
    optimal_slice (float): The optimal slice position in millimeters.
    """
    all_coords = []

    for s_coords in streamlines:
        s_coords = nib.affines.apply_affine(affine, s_coords)
        all_coords.append(s_coords)

    all_coords = np.concatenate(all_coords, axis=0)

    if plane == "sagittal":
        axis_coords = all_coords[:, 0]
    elif plane == "coronal":
        axis_coords = all_coords[:, 1]
    elif plane == "horizontal":
        axis_coords = all_coords[:, 2]

    # Find the slice with the maximum number of streamlines crossing it
    hist, bin_edges = np.histogram(axis_coords, bins=50)
    optimal_slice = bin_edges[np.argmax(hist)]

    return optimal_slice


def get_streamline_color(s_coords, cmap=None):
    """
    Calculate the color of a streamline based on its principal direction,
    where x, y, and z components correspond to red, green, and blue channels respectively.

    Parameters:
    s_coords (ndarray): Streamline coordinates of shape (n_points, 3).

    Returns:
    color (tuple): RGB color tuple for the streamline.
    """
    # Compute the mean direction vector from the start to the end of the streamline
    mean_direction = s_coords[-1] - s_coords[0]
    mean_direction = mean_direction / np.linalg.norm(
        mean_direction
    )  # Normalize the direction vector

    if cmap:
        scalar_value = np.abs(mean_direction[0])
        colormap = colormaps[cmap]
        color = colormap(scalar_value)  # Returns an RGBA tuple
    else:
        # Convert the direction vector into an RGB color
        # Each component of the mean direction corresponds to a color channel
        # Ensure the direction is within the range [0, 1] for color mapping
        r = np.abs(mean_direction[0])  # Red corresponds to x-direction
        g = np.abs(mean_direction[1])  # Green corresponds to y-direction
        b = np.abs(mean_direction[2])  # Blue corresponds to z-direction

        # Combine the components into an RGB color
        color = (r, g, b)

    return color


# def plot_streamlines_on_slice(
#     streamlines, affine, slice_mm, plane="coronal", ax=None, cmap="rainbow"
# ):
#     """
#     Plot streamlines on a 2D plane at a specific slice with an affine transformation, colored by mean direction.

#     Parameters:
#     streamlines (list of ndarray): List of streamlines, where each streamline is an ndarray of shape (n_points, 3).
#     affine (ndarray): Affine transformation matrix for converting voxel coordinates to real-world coordinates.
#     slice_mm (float): The position along the selected axis in millimeters to plot the slice.
#     plane (str, optional): The plane to plot ("sagittal", "coronal", "horizontal").
#     ax (matplotlib.axes.Axes, optional): The axis on which to plot. Creates new axis if None.

#     Returns:
#     ax: The axis with the streamlines plot applied.
#     """
#     if ax is None:
#         fig, ax = plt.subplots()

#     # Normalize for color mapping
#     norm = Normalize(vmin=-1, vmax=1)
#     cmap = plt.get_cmap(cmap)

#     for s_coords in streamlines:
#         # Compute the mean direction vector from the start to the end of the streamline
#         mean_direction = s_coords[-1] - s_coords[0]
#         mean_direction = mean_direction / np.linalg.norm(
#             mean_direction
#         )  # Normalize the direction vector

#         # Determine color based on the direction
#         color = cmap(
#             norm(mean_direction[0])
#         )  # Use one component (e.g., x-direction) to map color

#         x, y, z = s_coords[:, 0], s_coords[:, 1], s_coords[:, 2]

#         if plane == "sagittal":
#             mask = np.isclose(x, slice_mm, atol=1)
#             if np.any(mask):
#                 ax.plot(y[mask], z[mask], color=color, linewidth=0.1)
#             ax.set_xlabel("Y (mm)")
#             ax.set_ylabel("Z (mm)")

#         elif plane == "coronal":
#             mask = np.isclose(y, slice_mm, atol=1)
#             if np.any(mask):
#                 ax.plot(x[mask], z[mask], color=color, linewidth=0.1)
#             ax.set_xlabel("X (mm)")
#             ax.set_ylabel("Z (mm)")

#         elif plane == "horizontal":
#             mask = np.isclose(z, slice_mm, atol=1)
#             if np.any(mask):
#                 ax.plot(x[mask], y[mask], color=color, linewidth=0.1)
#             ax.set_xlabel("X (mm)")
#             ax.set_ylabel("Y (mm)")

#     ax.set_aspect("equal")
#     return ax


def plot_streamlines_on_slice(
    streamlines, affine, slice_mm, plane="coronal", ax=None, **kwargs
):
    """
    Plot streamlines on a 2D plane at a specific slice with an affine transformation, colored by directionality.

    Parameters:
    streamlines (list of ndarray): List of streamlines, where each streamline is an ndarray of shape (n_points, 3).
    affine (ndarray): Affine transformation matrix for converting voxel coordinates to real-world coordinates.
    slice_mm (float): The position along the selected axis in millimeters to plot the slice.
    plane (str, optional): The plane to plot ("sagittal", "coronal", "horizontal").
    ax (matplotlib.axes.Axes, optional): The axis on which to plot. Creates new axis if None.

    Returns:
    ax: The axis with the streamlines plot applied.
    """
    if ax is None:
        fig, ax = plt.subplots()

    for s_coords in streamlines:
        # Get the color based on the streamline direction
        color = get_streamline_color(s_coords)

        x, y, z = s_coords[:, 0], s_coords[:, 1], s_coords[:, 2]

        if plane == "sagittal":
            mask = np.isclose(x, slice_mm, atol=1)
            data1 = y[mask]
            data2 = z[mask]
            ax.set_xlabel("Y (mm)")
            ax.set_ylabel("Z (mm)")

        elif plane == "coronal":
            mask = np.isclose(y, slice_mm, atol=1)
            data1 = x[mask]
            data2 = z[mask]
            ax.set_xlabel("X (mm)")
            ax.set_ylabel("Z (mm)")

        elif plane == "horizontal":
            mask = np.isclose(z, slice_mm, atol=1)
            data1 = x[mask]
            data2 = y[mask]
            ax.set_xlabel("X (mm)")
            ax.set_ylabel("Y (mm)")

        if "linewidth" not in kwargs.keys():
            kwargs["linewidth"] = 0.1

        if np.any(mask):
            ax.plot(data1, data2, color=color, **kwargs)

    ax.set_aspect("equal")
    return ax
