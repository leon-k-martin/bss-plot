import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt


def plot_slice(
    bg_img,
    slice_mm,
    title=None,
    zero2nan=True,
    plane="sagittal",
    ax=None,
    interpolation="gaussian",
):
    """
    Plot a slice of the background image at the given slice position in real-world coordinates.

    Parameters:
    bg_img (Nifti1Image): The NIfTI image from which to extract the slice.
    slice_mm (float): The position along the selected axis in millimeters to plot the slice.
    title (str, optional): The title of the plot.
    zero2nan (bool, optional): Convert zeros to NaNs for transparency (default is True).
    plane (str, optional): The plane to plot ("sagittal", "coronal", "horizontal").

    Returns:
    fig, ax: Matplotlib figure and axis objects.
    """
    bg_data = bg_img.get_fdata()
    if zero2nan:
        bg_data = np.where(bg_data == 0, np.nan, bg_data)
    affine = bg_img.affine

    # Determine the slice index based on the selected plane
    if plane == "sagittal":
        slice_index = int(np.round((slice_mm - affine[0, 3]) / affine[0, 0]))
        y_coords = np.linspace(0, bg_data.shape[1] - 1, bg_data.shape[1])
        z_coords = np.linspace(0, bg_data.shape[2] - 1, bg_data.shape[2])
        y_realworld = nib.affines.apply_affine(
            affine,
            np.column_stack(
                [np.zeros_like(y_coords), y_coords, np.zeros_like(y_coords)]
            ),
        )[:, 1]
        z_realworld = nib.affines.apply_affine(
            affine,
            np.column_stack(
                [np.zeros_like(z_coords), np.zeros_like(z_coords), z_coords]
            ),
        )[:, 2]
        img_slice = np.flipud(bg_data[slice_index, :, :].T)
        extent = [y_realworld[0], y_realworld[-1], z_realworld[0], z_realworld[-1]]
        xlabel = "Y (mm)"
        ylabel = "Z (mm)"

    elif plane == "coronal":
        slice_index = int(np.round((slice_mm - affine[1, 3]) / affine[1, 1]))
        x_coords = np.linspace(0, bg_data.shape[0] - 1, bg_data.shape[0])
        z_coords = np.linspace(0, bg_data.shape[2] - 1, bg_data.shape[2])
        x_realworld = nib.affines.apply_affine(
            affine,
            np.column_stack(
                [x_coords, np.zeros_like(x_coords), np.zeros_like(x_coords)]
            ),
        )[:, 0]
        z_realworld = nib.affines.apply_affine(
            affine,
            np.column_stack(
                [np.zeros_like(z_coords), np.zeros_like(z_coords), z_coords]
            ),
        )[:, 2]
        img_slice = np.flipud(bg_data[:, slice_index, :].T)
        extent = [x_realworld[0], x_realworld[-1], z_realworld[0], z_realworld[-1]]
        xlabel = "X (mm)"
        ylabel = "Z (mm)"

    elif plane == "horizontal":
        slice_index = int(np.round((slice_mm - affine[2, 3]) / affine[2, 2]))
        x_coords = np.linspace(0, bg_data.shape[0] - 1, bg_data.shape[0])
        y_coords = np.linspace(0, bg_data.shape[1] - 1, bg_data.shape[1])
        x_realworld = nib.affines.apply_affine(
            affine,
            np.column_stack(
                [x_coords, np.zeros_like(x_coords), np.zeros_like(x_coords)]
            ),
        )[:, 0]
        y_realworld = nib.affines.apply_affine(
            affine,
            np.column_stack(
                [np.zeros_like(y_coords), y_coords, np.zeros_like(y_coords)]
            ),
        )[:, 1]
        img_slice = np.flipud(bg_data[:, :, slice_index].T)
        extent = [x_realworld[0], x_realworld[-1], y_realworld[0], y_realworld[-1]]
        xlabel = "X (mm)"
        ylabel = "Y (mm)"

    if not ax:
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.imshow(
        img_slice,
        cmap="gray",
        interpolation=interpolation,
        extent=extent,
    )
    if title:
        ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_aspect("equal")  # Aspect ratio of the plot
    ax.axis("on")  # Show axis with real-world coordinates
    return ax
