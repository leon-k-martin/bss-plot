import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import numpy.ma as ma
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
from nilearn import plotting
from scipy.ndimage import center_of_mass
from skimage.measure import find_contours


def get_cut_coords(nii_img):
    # Load the NIfTI image
    if isinstance(nii_img, str):
        nii_img = nib.load(nii_img)

    # Get the data array (voxel intensities)
    data = nii_img.get_fdata()

    # Calculate the center of mass in voxel coordinates
    com_voxel = center_of_mass(data)

    # Get the affine matrix
    affine = nii_img.affine

    # Convert the center of mass to real-world coordinates
    com_real_world = nib.affines.apply_affine(affine, com_voxel)

    return com_real_world


def get_com_slice(nii_img, plane="sagittal"):
    x, y, z = get_cut_coords(nii_img)

    if plane.lower() == "sagittal":
        return x
    elif plane.lower() == "coronal":
        return y
    elif plane.lower() == "horizontal":
        return z


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


def add_overlay(
    overlay_img,
    slice_mm,
    ax,
    alpha=0.9,
    threshold=10**-6,
    interpolation="gaussian",
    plane="sagittal",
    outline=False,
    outline_kwargs={"color": "k", "linewidth": 0.5, "alpha": 1},
    draw_contours=False,  # New parameter to draw contours instead of imshow
    contour_kwargs={"linewidths": 0.5, "levels": 10},  # Contour plot kwargs
    cmap="auto",
    zoom_in=True,
):
    """
    Apply an overlay from a NIfTI image onto an existing axis in real-world coordinates with thresholding.

    Parameters:
    ax (matplotlib.axes.Axes): The axis on which to apply the overlay.
    overlay_img (Nifti1Image): The overlay NIfTI image.
    slice_mm (float): The position along the selected axis in millimeters to plot the slice.
    cmap (str, optional): The colormap for the overlay.
    alpha (float, optional): Transparency level for the overlay.
    threshold (float, optional): The threshold below which values in the overlay are not displayed (transparent).
    plane (str, optional): The plane to plot ("sagittal", "coronal", "horizontal").
    outline (bool, optional): Whether to draw outline contours on the overlay.
    outline_kwargs (dict, optional): Keyword arguments for the outline plot.
    draw_contours (bool, optional): Whether to draw contours instead of using imshow.
    contour_levels (int or list, optional): Number or list of contour levels.
    contour_kwargs (dict, optional): Keyword arguments for the contour plot.

    Returns:
    overlay: The overlay artist (either a QuadMesh or a ContourSet depending on the method used).
    """
    xlim, ylim = ax.get_xlim(), ax.get_ylim()

    if isinstance(overlay_img, str):
        overlay_img = nib.load(overlay_img)
    overlay_data = overlay_img.get_fdata()
    overlay_affine = overlay_img.affine

    # Determine the colormap and normalization based on the data
    if cmap == "auto":
        if np.any(overlay_data < 0) and np.any(overlay_data > 0):
            # Data has both negative and positive values
            cmap = "RdBu_r"
            norm = mcolors.TwoSlopeNorm(
                vmin=np.min(overlay_data), vcenter=0, vmax=np.max(overlay_data)
            )
        elif np.all(overlay_data < 0):
            # All data is negative
            cmap = "Blues"
            norm = None  # No need to center for all negative values
        else:
            # All data is positive
            cmap = "Reds"
            norm = None  # No need to center for all positive values
    else:
        norm = None

    # Determine the slice index based on the selected plane
    if plane == "sagittal":
        slice_index = int(
            np.round((slice_mm - overlay_affine[0, 3]) / overlay_affine[0, 0])
        )
        y_coords = np.linspace(0, overlay_data.shape[1] - 1, overlay_data.shape[1])
        z_coords = np.linspace(0, overlay_data.shape[2] - 1, overlay_data.shape[2])
        y_realworld = nib.affines.apply_affine(
            overlay_affine,
            np.column_stack(
                [np.zeros_like(y_coords), y_coords, np.zeros_like(y_coords)]
            ),
        )[:, 1]
        z_realworld = nib.affines.apply_affine(
            overlay_affine,
            np.column_stack(
                [np.zeros_like(z_coords), np.zeros_like(z_coords), z_coords]
            ),
        )[:, 2]
        overlay_slice = np.flipud(overlay_data[slice_index, :, :].T)
        extent = [y_realworld[0], y_realworld[-1], z_realworld[0], z_realworld[-1]]

    elif plane == "coronal":
        slice_index = int(
            np.round((slice_mm - overlay_affine[1, 3]) / overlay_affine[1, 1])
        )
        x_coords = np.linspace(0, overlay_data.shape[0] - 1, overlay_data.shape[0])
        z_coords = np.linspace(0, overlay_data.shape[2] - 1, overlay_data.shape[2])
        x_realworld = nib.affines.apply_affine(
            overlay_affine,
            np.column_stack(
                [x_coords, np.zeros_like(x_coords), np.zeros_like(x_coords)]
            ),
        )[:, 0]
        z_realworld = nib.affines.apply_affine(
            overlay_affine,
            np.column_stack(
                [np.zeros_like(z_coords), np.zeros_like(z_coords), z_coords]
            ),
        )[:, 2]
        overlay_slice = np.flipud(overlay_data[:, slice_index, :].T)
        extent = [x_realworld[0], x_realworld[-1], z_realworld[0], z_realworld[-1]]

    elif plane == "horizontal":
        slice_index = int(
            np.round((slice_mm - overlay_affine[2, 3]) / overlay_affine[2, 2])
        )
        x_coords = np.linspace(0, overlay_data.shape[0] - 1, overlay_data.shape[0])
        y_coords = np.linspace(0, overlay_data.shape[1] - 1, overlay_data.shape[1])
        x_realworld = nib.affines.apply_affine(
            overlay_affine,
            np.column_stack(
                [x_coords, np.zeros_like(x_coords), np.zeros_like(x_coords)]
            ),
        )[:, 0]
        y_realworld = nib.affines.apply_affine(
            overlay_affine,
            np.column_stack(
                [np.zeros_like(y_coords), y_coords, np.zeros_like(y_coords)]
            ),
        )[:, 1]
        overlay_slice = np.flipud(overlay_data[:, :, slice_index].T)
        extent = [x_realworld[0], x_realworld[-1], y_realworld[0], y_realworld[-1]]

    # Apply the threshold by creating a masked array
    if threshold is not None:
        overlay_slice = np.where(
            np.abs(overlay_slice) < threshold, np.nan, overlay_slice
        )

    if draw_contours:
        # Draw contours instead of using imshow
        overlay = ax.contour(
            overlay_slice,
            extent=extent,
            cmap=cmap,
            **contour_kwargs,
        )
    else:
        # Plot the overlay onto the existing axis
        overlay = ax.imshow(
            overlay_slice,
            cmap=cmap,
            alpha=alpha,
            interpolation=interpolation,
            extent=extent,
            norm=norm,  # Apply the norm for correct color scaling
        )

    if outline:
        # Use skimage to find contours
        contours = find_contours(np.nan_to_num(overlay_slice), level=threshold)
        for contour in contours:
            # Calculate the extent range in terms of the slice shape
            interp_x = np.linspace(extent[0], extent[1], overlay_slice.shape[1])
            interp_y = np.linspace(extent[2], extent[3], overlay_slice.shape[0])

            real_world_contour = np.column_stack(
                [
                    np.interp(
                        contour[:, 1], np.arange(overlay_slice.shape[1]), interp_x
                    ),
                    np.interp(
                        contour[:, 0], np.arange(overlay_slice.shape[0]), interp_y
                    ),
                ]
            )
            ax.plot(
                real_world_contour[:, 0], real_world_contour[:, 1], **outline_kwargs
            )  # Adjust color as needed

    if not zoom_in:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    return overlay
