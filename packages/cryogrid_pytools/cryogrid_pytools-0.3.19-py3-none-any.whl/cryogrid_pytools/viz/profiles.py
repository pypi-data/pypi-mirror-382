import matplotlib.pyplot as plt
import xarray as xr
from matplotlib.axes import Axes as _Axes
from matplotlib.figure import Figure as _Figure


def plot_profiles(
    ds_profile: xr.Dataset, figsize=(12, 9)
) -> tuple[_Figure, list[_Axes], list]:
    """
    Plots the profiles of the variables in the dataset that is read in with
    read_OUT_regridded_FCI2_clusters.

    Parameters
    ----------
    ds_profile : xr.Dataset
        The dataset containing the profiles to be plotted. Must contain the
        following variables: 'T', 'water', 'ice', 'class_number'.

    Returns
    -------
    tuple[matplotlib.figure.Figure, list[matplotlib.axes.Axes], list]
        The figure, axes and images created by the plotting function.
    """

    # doing a bunch of checks before trying to plot
    assert ds_profile.profile.size == 1, (
        "More than one profile found in dataset. Make sure that you're passing only one profile file pattern."
    )
    assert "T" in ds_profile, "Temperature profile not found in dataset."
    assert "water" in ds_profile, "Water content profile not found in dataset."
    assert "ice" in ds_profile, "Ice content profile not found in dataset."

    profile = ds_profile.profile.item()

    ds_profile = ds_profile.compute()
    # for now, the plot is static in its L x W
    fig, axs = plt.subplots(
        3,
        1,
        figsize=figsize,
        sharex=True,
        sharey=True,
        dpi=120,
        subplot_kw=dict(facecolor="0.8"),
    )
    axs = list(axs.ravel())

    imgs = []
    imgs += (
        plot_profile(
            ds_profile.T.assign_attrs({"long_name": "temperature", "units": "°C"}),
            ax=axs[0],
            center=0,
            cmap="RdBu_r",
        ),
    )
    imgs += (
        plot_profile(
            ds_profile.water.assign_attrs({"long_name": "Water content", "units": "%"}),
            ax=axs[1],
            cmap="Greens",
        ),
    )
    imgs += (
        plot_profile(
            ds_profile.ice.assign_attrs({"long_name": "Ice content", "units": "%"}),
            ax=axs[2],
            cmap="Blues",
        ),
    )

    [ax.set_title("") for ax in axs]
    axs[0].set_title(f"Profiles at profile #{profile}", loc="left")

    fig.tight_layout()

    return fig, axs, imgs


def plot_profile(da_profile: xr.DataArray, **kwargs):
    """
    Plots a profile of a given DataArray using da.plot.imshow

    Parameters
    ----------
    da_profile : xr.DataArray
        The profile to be plotted.
    **kwargs
        Additional keyword arguments to be passed to the plotting function.

    Returns
    -------
    matplotlib.image.AxesImage
        The image object created by the plotting function.
        With the following attributes:
        - figure: The figure object that contains the image.
        - axes: The axes object that contains the image.
        - colorbar: The colorbar object that is associated with the image.
    """

    dims = da_profile.sizes
    if "profile" in dims:
        if dims["profile"] != 1:
            raise ValueError(
                "More than one profile found in dataset. Make sure that you're passing only one profile file pattern."
            )
        else:
            da_profile = da_profile.isel(profile=0)

    if "depth" not in dims:
        if "depth" in da_profile.coords and "level" in dims:
            da_profile = da_profile.set_index(level="depth").rename(level="depth")
        else:
            raise ValueError(
                "Depth coordinate not found in dataset. Make sure that you're passing a profile dataset."
            )

    name = da_profile.name

    long_name = da_profile.attrs.get("long_name", name)
    long_name = long_name.replace("_", " ").capitalize()

    unit = da_profile.attrs.get("units", "")
    unit = f"[{unit}]" if unit else ""

    kwargs["cbar_kwargs"] = dict(label=f"{long_name} {unit}", pad=0.01) | kwargs.pop(
        "cbar_kwargs", {}
    )

    if "ax" in kwargs:
        props = dict(robust=True) | kwargs
    else:
        props = dict(robust=True, aspect=4, size=3.5, center=0) | kwargs

    img = da_profile.plot.imshow(**props)
    img.axes.set_xlabel("")
    img.axes.set_ylabel("Depth [m]")

    title = f"{long_name} profile #{da_profile.profile.item()}"
    img.axes.set_title("", loc="center")
    img.axes.set_title(title, loc="left")

    return img
