#!/usr/bin/env python3
# Standard/external imports
from __future__ import annotations
from typing import *
import numpy as np
import numpy.typing as npt
from scipy import interpolate
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from matplotlib.markers import MarkerStyle
import gsw
import cmocean

# Module imports
from pyrsktools.datatypes import *
from pyrsktools.channels import *

if TYPE_CHECKING:
    from matplotlib.colors import Colormap
    from pyrsktools import RSK


def _channelsubplots(
    data: npt.NDArray,
    channelNames: List[str],
    channelUnits: List[str],
    prettyNames: List[str] = None,
) -> Tuple[plt.Figure, List[plt.Axes]]:
    if not prettyNames:
        prettyNames = channelNames
    else:
        assert len(channelNames) == len(prettyNames)

    fig, axes = plt.subplots(len(channelNames), 1)
    axes = axes if hasattr(axes, "__len__") else list([axes])
    for i in range(len(channelNames)):
        axes[i].plot(
            data["timestamp"], data[channelNames[i]], label=f"{prettyNames[i]} ({channelUnits[i]})"
        )
        axes[i].set_title(prettyNames[i])
        axes[i].set_ylabel(channelUnits[i])

        if "depth" in channelNames[i]:
            axes[i].invert_yaxis()

    return fig, axes


def _addCastPatches(
    data: npt.NDArray,
    profileRegions: List[Tuple[RegionCast, RegionCast, RegionProfile]],
    channelNames: List[str],
    axes: List[plt.Axes],
) -> None:
    for i in range(len(channelNames)):
        cmax = 1.01 * np.max(data[channelNames[i]])
        cmin = 1.01 * np.min(data[channelNames[i]])
        for firstcast, secondcast, _ in profileRegions:
            if firstcast.isdowncast():
                downcast = firstcast
                upcast = secondcast
            else:
                downcast = secondcast
                upcast = firstcast

            start, end = mdates.date2num(downcast.tstamp1), mdates.date2num(downcast.tstamp2)
            axes[i].add_patch(
                mpatches.Rectangle(
                    (start, cmin), end - start, cmax, alpha=0.2, fc="white", ec="black"
                ),
            )
            start, end = mdates.date2num(upcast.tstamp1), mdates.date2num(upcast.tstamp2)
            axes[i].add_patch(
                mpatches.Rectangle(
                    (start, cmin), end - start, cmax, alpha=0.2, fc="gray", ec="black"
                ),
            )


def plotdata(
    self: RSK,
    channels: Union[str, Collection[str]] = [],
    profile: Optional[int] = None,
    direction: str = "down",
    showcast: bool = False,
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """Plot a time series of logger data.

    Args:
        channels (Union[str, Collection[str]], optional): longName of channel(s) to plot, can be multiple in
            a cell. Defaults to [] (plot all available channels).
        profile (int, optional): profile number. Defaults to None (ignores profiles and plot as time series).
        direction (str, optional): cast direction of either "up" or "down". Defaults to "down".
        showcast (bool, optional): show cast direction when set as true. It is recommended to show the cast
            direction patch for time series data only. This argument will not work when pressure and sea
            pressure channels are not available. Defaults to False.

    Returns:
        Tuple[plt.Figure, List[plt.Axes]]: a two-element tuple containing the related figure and list of axes respectively.

    This method plots the channels specified by ``channels`` as a time series. If a channel is not specified,
    then this method will plot them all. If the current RSK instance has profiles (e.g., via :meth:`RSK.computeprofiles`),
    then users may specify a single profile and direction to plot. In this case, however, this method can only
    plot one cast and direction at a time. If you want to compare many profiles, then use either :meth:`RSK.plotprofiles`
    or :meth:`RSK.mergeplots`.

    The output tuple containing ``handles`` and ``axes`` are lists of chart line objects and axes which contain
    the properties of each subplot.

    The command below creates the plot below it:

    >>> with RSK("example.rsk") as rsk:
    ... rsk.readdata()
    ... fig, axes = rsk.plotdata(channels=["conductivity", "temperature", "dissolved_o2_saturation", "chlorophyll"])
    ... plt.show()

    .. figure:: /img/plotdata_1.png
        :scale: 70%
        :alt: first plot data plot

        The figure above is the output of :meth:`RSK.plotdata`, where each subplot created
        relates to the labels given to :obj:`RSK.data` columns and the :obj:`RSK.channels` attribute.


    This method has an option to overlay cast detection events on top of the pressure time series.
    This is particularly useful to ensure that the profile detection events correctly demarcate the profiles.

    The command below plots a time series of pressure with cast detection events overlaid:

    >>> fig, axes = rsk.plotdata(channels="pressure", showcast=True)
    ... plt.show()

    .. figure:: /img/plotdata_2.png
        :scale: 65%
        :alt: second plot data plot

        The figure above is the output of :meth:`RSK.plotdata` when ``showcast`` option is on
        with the pressure channel.
    """
    self.dataexistsorerror()
    self.channelsexistorerror(channels)

    if direction not in ("up", "down"):
        raise ValueError(
            f"Invalid direction: {direction}. If trying to plot multiple casts or directions, see RSK.plotprofiles()."
        )

    profileRegions = None
    if not self.getregionsbytypes([RegionCast, RegionProfile]):
        data = self.data
    else:
        # List of tuples: (RegionCast, RegionCast, RegionProfile)
        profileRegions = self.getprofilesorerror()

        if profile is not None:
            if profile > len(profileRegions) - 1:
                ValueError(f"Profile out of range: {profile}")

            p = profileRegions[profile][2]  # Get the RegionProfile out of the 3-element tuple
            data = self.data[
                np.logical_and(
                    self.data["timestamp"] >= p.tstamp1, self.data["timestamp"] <= p.tstamp2
                )
            ]
            # Change profileRegions to contain only the one user-specified profile
            profileRegions = profileRegions[profile : profile + 1]
        else:
            data = self.data

    channelNames, channelUnits = self.getchannelnamesandunits(channels)
    prettyNames = self.getdbnamesfromlongnames(channelNames)

    fig, axes = _channelsubplots(data, channelNames, channelUnits, prettyNames)
    assert len(axes) == len(channelNames)

    fig.subplots_adjust(left=0.08, bottom=0.08, right=0.95, top=0.93, hspace=1)
    if profile is not None:
        fig.legend(
            title=f"Profile number: {profile}\nCast direction: {direction}",
            loc="center right",
            borderaxespad=0.1,
        )
        fig.subplots_adjust(left=0.08, bottom=0.08, right=0.87, top=0.93, hspace=1)

    if showcast:
        if profileRegions:
            _addCastPatches(data, profileRegions, channelNames, axes)
        fig.legend(
            handles=[mpatches.Patch(fc="white", ec="black"), mpatches.Patch(fc="gray", ec="black")],
            labels=["downcast", "upcast"],
            loc="center right",
            borderaxespad=0.1,
        )
        fig.subplots_adjust(left=0.08, bottom=0.08, right=0.87, top=0.93, hspace=1)

    return fig, axes


def plotprofiles(
    self: RSK,
    channels: Union[str, Collection[str]] = [],
    profiles: Union[int, Collection[int]] = [],
    direction: str = "both",
    reference: str = "sea_pressure",
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """Plot summaries of logger data as profiles.

    Args:
        channels (Union[str, Collection[str]], optional): longName of channel(s) to plot, can be multiple in
            a cell. Defaults to [] (all available channels).
        profiles (Union[int, Collection[int]], optional): profile sequence(s). Defaults to [] (all profiles).
        direction (str, optional): cast direction: "up", "down", or "both". When choosing "both",
            downcasts are plotted with solid lines and upcasts are plotted with dashed lines.
            Defaults to "both".
        reference (str, optional): Channel plotted on the y axis for each subplot.
            Options are "sea_pressure", "depth", or "pressure".
            Defaults to "sea_pressure".

    Returns:
        Tuple[plt.Figure, List[plt.Axes]]: a two-element tuple containing the related figure and list of axes respectively.

    Generates a subplot for each ``channels`` versus selected reference, using the data elements in the :obj:`.RSK.data` field.
    If no ``channels`` are specified, it will plot them all as individual subplots.

    When ``direction`` is set to 'both', downcasts are plotted with solid lines and upcasts are plotted with dashed lines.

    The output ``handles`` is a vector of chart line objects containing the properties of each subplot.

    The code below produced the plot below it:

    >>> with RSK("example.rsk") as rsk:
    ...    rsk.readdata()
    ...    rsk.deriveseapressure()
    ...    rsk.derivesalinity()
    ...
    ...    fig, axes = rsk.plotprofiles(
    ...        channels=["conductivity", "temperature", "salinity"],
    ...        profiles=range(0, 3),
    ...        direction="down",
    ...    )
    ...    plt.show()

    .. figure:: /img/plotprofiles_1.png
        :scale: 75%
        :alt: plot profiles plot

        The figure above is the profiles plotted using :meth:`RSK.plotprofiles`.
        Selecting conductivity, temperature, and salinity channels facilitates comparison.
    """
    self.dataexistsorerror()
    self.channelsexistorerror(channels)
    self.channelsexistorerror(reference)

    if direction not in ("up", "down", "both"):
        raise ValueError(f"Invalid direction: {direction}")

    referenceChannels = {SeaPressure.longName, Pressure.longName, Depth.longName}
    if reference not in referenceChannels:
        raise ValueError(
            f"Invalid reference channel: {reference}. Must be one of: {', '.join(referenceChannels)}."
        )

    # If user gave "both", we need up and down separately so we can display
    # them differently on our plot. If "both", create a list of tuples
    # containing up and down profile indices, otherwise keep as a normal list.
    if direction == "both":
        up = self.getprofilesindices(profiles, "up")
        down = self.getprofilesindices(profiles, "down")
        if len(up) == len(down):
            profileIndices = [(up[i], down[i]) for i in range(len(up))]
        else:
            profileIndices = [(up[i], down[i]) for i in range(min(len(up), len(down)))]
            lastprofile: list = up[-1] if len(up) > len(down) else down[-1]
            profileIndices.append([lastprofile, []])  # type:ignore

    else:
        profileIndices = self.getprofilesindices(profiles, direction)

    channelNames, channelUnits = self.getchannelnamesandunits(channels, exclude=referenceChannels)
    if len(channelNames) == 0:
        raise ValueError(
            f"All channels to plot exist within the set of reference channels ({', '.join(referenceChannels)}). Try RSK.plotdata() instead."
        )
    # Pretty names for titles/labels
    prettyNames = self.getdbnamesfromlongnames(channelNames)
    formattedReference = self.getdbnamesfromlongnames(reference)[0]

    Y = self.data[reference]
    refUnits = [c.units for c in self.channels if c.longName == reference][0]

    fig, axes = plt.subplots(1, len(channelNames), figsize=(4.8, 6.8))
    axes = axes if hasattr(axes, "__len__") else np.array([axes])

    assert len(axes) == len(channelNames)

    for i in range(len(channelNames)):
        axes[i].set_title(prettyNames[i])
        axes[i].set_xlabel(channelUnits[i])
        axes[i].set_ylabel(f"{formattedReference} [{refUnits}]")
        axes[i].invert_yaxis()
        label = f"{prettyNames[i]} ({channelUnits[i]})"

        for indices in profileIndices:
            if direction == "both":
                upIndices = indices[0]
                axes[i].plot(
                    self.data[channelNames[i]][upIndices], Y[upIndices], linestyle="--", label=label
                )
                downIndices = indices[1]
                axes[i].plot(
                    self.data[channelNames[i]][downIndices],
                    Y[downIndices],
                    linestyle="-",
                    label=label,
                )
            else:
                axes[i].plot(self.data[channelNames[i]][indices], Y[indices], label=label)

    # Increase spacing to avoid overlapping labels
    fig.subplots_adjust(left=0.12, right=0.95, wspace=0.85)
    return fig, axes


def _getcolormap(channelName: str) -> Colormap:
    if channelName == Temperature.longName:
        return cmocean.cm.thermal
    elif channelName == Chlorophyll.longName:
        return cmocean.cm.algae
    elif channelName == Backscatter.longName:
        return cmocean.cm.matter
    elif channelName == Phycoerythrin.longName:
        return cmocean.cm.turbid
    else:
        return cmocean.cm.haline


def images(
    self: RSK,
    channels: Union[str, Collection[str]] = [],
    profiles: Union[int, Collection[int]] = [],
    direction: str = "down",
    reference: str = "sea_pressure",
    showgap: bool = False,
    threshold: Optional[float] = None,
    image: Optional[Image] = None,
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """Plot profiles in a 2D plot.

    Args:
        channels (Union[str, Collection[str]], optional): longName of channel(s) to plot, can be multiple in
            a cell. Defaults to [] (all available channels).
        profiles (Union[int, Collection[int]], optional): profile sequence(s). Defaults to [] (all profiles).
        direction (str, optional): cast direction of either "up" or "down". Defaults to "down".
        reference (str, optional): Channel that will be plotted as y. Can be any channel. Defaults to "sea_pressure".
        showgap (bool, optional): Plotting with interpolated profiles onto a regular time grid, so that gaps
            between each profile can be shown when set as true. Defaults to False.
        threshold (float, optional): Time threshold in seconds to determine the maximum gap
            length shown on the plot. Any gap smaller than the threshold will not show.
            Defaults to None.
        image: (Image, optional): optional pre-computed/customized image generated by :meth:`RSK.generate2D`. Defaults to None.

    Returns:
        Tuple[plt.Figure, List[plt.Axes]]: a two-element tuple containing the related figure and list of axes respectively.

    This function produces a heat map of any specified channel. The x-axis is always time, and the y-axis is the ``reference`` channel
    argument, which is commonly depth or sea_pressure, but can be any channel (default is sea_pressure).
    Each profile must be gridded onto the same ``reference`` channel, which is accomplished with :meth:`RSK.binaverage`.

    Example:

    >>> fig, axes = rsk.images(channels="chlorophyll", direction="up")
    ... plt.show()

    .. figure:: /img/RSKimages_1.png
        :scale: 80%
        :alt: first images plot

        The cmocean toolbox (`link <https://matplotlib.org/cmocean/>`_)
        provides colormaps like the one used in the plot above. This one is designed to plot cholorophyll.

    Users can customize the length of the time gaps over which the data are interpolated with the threshold input parameter.
    This method calls :meth:`RSK.generate2D` to generate data for visualization unless the user provides one via the ``image`` argument.
    An :class:`.Image` instance contains x, y and data fields for users' convenience to render the plot as they like.

    Below are two examples of how to use the showgap parameter.

    To plot the data with the gaps intact:

    >>> fig, axes= rsk.images(channels="temperature", direction="down", showgap=True)
    ... plt.show()

    .. image:: /img/RSKimages_2.png
        :scale: 50%
        :align: center
        :alt: second images plot

    To fill all of the gaps longer than 6 minutes with interpolated values:

    >>> fig, axes = rsk.images(channels="temperature", direction="down", showgap=True, threshold=360.0)
    ... plt.show()

    .. image:: /img/RSKimages_3.png
        :scale: 50%
        :align: center
        :alt: third images plot
    """
    self.dataexistsorerror()
    self.channelsexistorerror(channels)
    self.channelsexistorerror(reference)

    if direction not in ("up", "down"):
        raise ValueError(f"Invalid direction: {direction}")

    if image is not None:
        if not isinstance(image, Image):
            raise TypeError(f"Argument 'image' must be of type Image but got: {type(image)}")
        img = image
    else:
        img = self.generate2D(channels, profiles, direction, reference)

    fig, axes = plt.subplots(len(img.channelNames), 1)
    axes = axes if hasattr(axes, "__len__") else [axes]

    assert len(axes) == len(img.channelNames)
    # Pretty names for titles/labels
    prettyNames = self.getdbnamesfromlongnames(img.channelNames)
    referenceName = self.getdbnamesfromlongnames(img.reference)[0]

    for i in range(len(img.channelNames)):
        axes[i].set_title(f"{prettyNames[i]} ({img.channelUnits[i]})  {img.x[0]} - {img.x[-1]}")
        axes[i].set_xlabel(f"Time (UTC)")
        axes[i].set_ylabel(f"{referenceName} ({img.referenceUnit})")
        axes[i].invert_yaxis()

        binValues = img.data[:, :, i]

        colormap = _getcolormap(img.channelNames[i])
        colormap.alpha = np.isfinite(binValues)
        if not showgap:
            plot = axes[i].pcolor(
                img.x,
                img.y,
                binValues,
                shading="auto",
                cmap=colormap,
                edgecolors="none",
            )
        else:
            x = img.x.astype(np.uint64)
            unitTime = min(
                abs((x[:-1] - x[1:]).astype(np.int64))
            )  # select the smallest time space between two profiles as unitTime
            n = np.round((x[-1] - x[0]) / unitTime).astype(np.int64)
            xItp = np.linspace(x[0], x[-1], n)  # rebuild the time
            indItp = np.ones((1, x.size))

            for k in range(x.size):
                indMt = abs(xItp - x[k])
                indItp[0, k] = indMt.argmin(0)

            indNan = np.setxor1d(indItp, np.arange(0, xItp.size)).astype(np.int64)

            binValues_itp = np.empty([binValues.shape[0], xItp.size])
            for ii in range(binValues.shape[0]):
                binValues_itp[ii, :] = np.interp(xItp, x, binValues[ii, :])
            binValues_itp[:, indNan] = np.nan

            if threshold:
                diffIndices = np.diff(indItp)
                gapIndices = np.flatnonzero(diffIndices > 1)
                removeGapIndices = []
                for g in gapIndices:
                    tmpIndex = np.arange(indItp[0, g] + 1, indItp[0, g] + 1 + diffIndices[0, g] - 1)
                    if tmpIndex.size * unitTime / 1000 < threshold:
                        for tmp in tmpIndex:
                            removeGapIndices.append(int(tmp))
                if len(removeGapIndices) > 0:
                    binValues_itp = np.delete(binValues_itp, removeGapIndices, 1)
                    xItp = np.delete(xItp, removeGapIndices, 0)

            xItp = xItp.astype("datetime64[ms]")
            plot = axes[i].pcolor(
                xItp,
                img.y,
                binValues_itp,
                shading="auto",
                cmap=colormap,
                edgecolors="none",
            )

        fig.colorbar(plot)

    # Increase spacing to avoid overlapping labels
    fig.subplots_adjust(left=0.15, right=1.0, wspace=0.85)
    return fig, axes


def plotTS(
    self: RSK,
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "both",
    isopycnal: Union[int, Collection[int]] = 5,
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot a TS diagram in terms of Practical Salinity and Potential Temperature.

    Args:
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to [] (all available profiles).
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".
        isopycnal (Union[int, Collection[int]], optional): number of isopycnals to show on the plot, or
            a list containing desired isopycnals. Defaults to 5.

    Returns:
        Tuple[plt.Figure, plt.Axes]: a two-element tuple containing the related figure and axes of the plot.

    Plots potential temperature as a function of Practical Salinity using 0 dbar as a reference.
    Potential density anomaly contours are drawn automatically. :meth:`RSK.plotTS` requiresTEOS-10 GSW toolkit. If the data is stored as a time series,
    then each point will be coloured according to the time and date it was taken. If the data is organized into profiles,
    then each profile is plotted with a different colour.

    NOTE: Absolute Salinity is computed internally because it is required for potential temperature and potential density.
    Here it is assumed that the Absolute Salinity (SA) anomaly is zero so that SA = SR (Reference Salinity).
    This is probably the best approach in many coastal regions where the Absolute Salinity anomaly is not well known
    (see http://www.teos-10.org/pubs/TEOS-10_Primer.pdf).

    Example:

    >>> fig, axes = rsk.plotTS(profiles=range(3), direction="down", isopycnal=10)
    ... plt.show()

    .. figure:: /img/plotTS_1.png
        :scale: 50%
        :alt: plotTS plot

        The figure above is T-S diagram plotted using :meth:`RSK.plotTS`, where each downcast is plotted with a different colour.
        :meth:`RSK.plotTS` outputs ``handles`` to the line objects so that users can customize the curves.
    """
    self.dataexistsorerror()
    self.channelsexistorerror([Salinity, Temperature])
    if not self.channelexists(SeaPressure):
        self.deriveseapressure()

    if direction not in ("up", "down", "both"):
        raise ValueError(f"Invalid direction: {direction}")

    seaPressure = self.data[SeaPressure.longName]
    salinity = self.data[Salinity.longName]
    temperature = self.data[Temperature.longName]

    profileIndices = {}
    if direction == "both":
        profileIndices["up"] = self.getprofilesindices(profiles, "up")
        profileIndices["down"] = self.getprofilesindices(profiles, "down")
        assert len(profileIndices["up"]) == len(profileIndices["down"])
    else:
        profileIndices[direction] = self.getprofilesindices(profiles, direction)

    fig, axes = plt.subplots(1, 1)
    markerStyle = MarkerStyle("o", "none")

    aSMin: Optional[float] = None
    for direction, directionIndices in profileIndices.items():
        for i, indices in enumerate(directionIndices):
            seaPressure = self.data[SeaPressure.longName][indices]
            salinity = self.data[Salinity.longName][indices]
            temperature = self.data[Temperature.longName][indices]

            absoluteSalinity = gsw.SR_from_SP(salinity)  # assume delta SA = 0, SA ~= SR
            conservativeTemperature = gsw.CT_from_t(absoluteSalinity, temperature, seaPressure)

            if aSMin is None:
                aSMin = np.min(absoluteSalinity)
                aSMax = np.max(absoluteSalinity)
                cTMin = np.min(conservativeTemperature)
                cTMax = np.max(conservativeTemperature)
            else:
                aSMin = min(aSMin, np.min(absoluteSalinity))
                aSMax = max(aSMin, np.max(absoluteSalinity))
                cTMin = min(cTMin, np.min(conservativeTemperature))
                cTMax = max(cTMax, np.max(conservativeTemperature))

            axes.scatter(
                salinity, conservativeTemperature, marker=markerStyle, label=f"{direction}cast {i}"
            )

    aSAxis = np.arange(aSMin - 0.2, aSMax + 0.2, (aSMax - aSMin) / 200)
    cTAxis = np.arange(cTMin - 0.2, cTMax + 0.2, (cTMax - cTMin) / 200)
    aSAxis[aSAxis < 0] = np.nan
    [aSGridded, cTGridded] = np.meshgrid(aSAxis, cTAxis)
    isopycsGridded = gsw.sigma0(aSGridded, cTGridded)  # Potential density
    salinityGridded = gsw.SP_from_SR(aSGridded)
    contour = axes.contour(
        salinityGridded,
        cTGridded,
        isopycsGridded,
        isopycnal,
        linestyles="dotted",
        cmap="gray",
        alpha=0.5,
    )
    axes.clabel(contour, fontsize=9, inline=True)
    axes.legend(loc="best", borderaxespad=0.1)
    axes.set_title(r"$\theta_0$-S Diagram")
    axes.set_xlabel("Practical Salinity")
    tUnits = [c.units for c in self.channels if c.longName == Temperature.longName][0]
    axes.set_ylabel(f"Conservative Temperature ({tUnits})")

    return fig, axes


def plotprocesseddata(
    self: RSK, channels: Union[str, Collection[str]] = []
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """Plot summaries of logger burst data.

    Args:
        channels (Union[str, Collection[str]], optional): longName of channel(s) to plot, can be multiple in
            a cell, if no value is given it will plot all channels. Defaults to [] (all available channels).

    Returns:
        Tuple[plt.Figure, List[plt.Axes]]: a two-element tuple containing the related figure and list of axes respectively.

    Plots the processedData initially read by :meth:`RSK.readprocesseddata`.

    It creates a subplot for every channel available, unless the channel argument is used to select a subset.

    The code below provides example usage and a resulting plot.

    >>> with RSK("example.rsk") as rsk:
    ...     t1, t2 = np.datetime64("2020-10-03T11:30:00"), np.datetime64("2020-10-03T19:20:00")
    ...     rsk.readdata(t1=t1, t2=t2)
    ...     rsk.readprocesseddata(t1=t1, t2=t2)
    ...
    ...     fig, axes = rsk.mergeplots(
    ...         rsk.plotprocesseddata(channels="pressure"),
    ...         rsk.plotdata(channels="pressure"),
    ...     )
    ...     plt.show()

    .. figure:: /img/RSKplotprocesseddata_1.png
        :scale: 60%
        :alt: plot burst data plot

        In the figure above, the blue line shows the values in the :obj:`RSK.processedData` field
        and the purple line shows those from the :obj:`RSK.data` field.
    """
    self.dataexistsorerror(processedData=True)
    self.channelsexistorerror(channels, processedData=True)

    channelNames, channelUnits = self.getchannelnamesandunits(channels, processedData=True)
    # Pretty names for titles/labels
    prettyNames = self.getdbnamesfromlongnames(channelNames)

    fig, axes = _channelsubplots(self.processedData, channelNames, channelUnits, prettyNames)

    assert len(axes) == len(channelNames)

    fig.subplots_adjust(left=0.08, bottom=0.08, right=0.95, top=0.93, hspace=1)

    return fig, axes


def mergeplots(
    plottuple1: Tuple[plt.Figure, List[plt.Axes]],
    plottuple2: Tuple[plt.Figure, List[plt.Axes]],
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """Merge two plots via their associated figure and axes objects.

    Args:
        plottuple1 (Tuple[plt.Figure, List[plt.Axes]]): tuple containing the figure and axes list of the first plot
        plottuple2 (Tuple[plt.Figure, List[plt.Axes]]): tuple containing the figure and axes list of the second plot

    Returns:
        Tuple[plt.Figure, List[plt.Axes]]: an updated figure and axes list relating to the merged plot

    Expects two tuples, each of which contains a figure as its first tuple-element and a list of axes
    as its second element. The lines from the first plot will be maintained (including their marker style and colour),
    while the lines from the second will be merged onto the first plot with a solid marker style and random colour.

    See :meth:`plotprocesseddata` for example usage.
    """
    fig1, axes1 = plottuple1[0], plottuple1[1]
    fig2, axes2 = plottuple2[0], plottuple2[1]

    if len(axes1) != len(axes2):
        raise ValueError(f"Len of axes1 ({len(axes1)}) must match len of axes2 ({len(axes2)}).")

    plt.close(fig2)

    # If the user calls this method twice (e.g., to merge 3+ plots), the
    # plot legend will be drawn more than once.
    # Let's remove all legends except the misc. ones, e.g.,
    # those that plot profile outlines.

    fig1.legends = [
        legend
        for legend in fig1.legends
        for text in legend.get_texts()
        if text.get_text() in {"downcast", "upcast"}
    ]

    for i in range(len(axes1)):
        tmpAx = axes1[i]
        for line in axes2[i].get_lines():
            x = line.get_xdata()
            y = line.get_ydata()
            tmpAx.plot(x, y, c=np.random.random(3), label=line.get_label())
            tmpAx.set_title(f"{axes1[i].get_title()} + {axes2[i].get_title()}")
            tmpAx.set_ylabel(
                ""
            )  # Remove y label to avoid displaying two different y labels, instead we will display a legend (see below)

        fig1.delaxes(axes1[i])
        fig1.add_axes(tmpAx)

    plt.legend()
    return fig1, fig1.get_axes()
