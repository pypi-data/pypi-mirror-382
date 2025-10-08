#!/usr/bin/env python3
# Standard/external imports
from __future__ import annotations
from optparse import Values
from time import time
from typing import *
import numpy as np
import numpy.typing as npt
from numpy.lib import recfunctions as rfn
from scipy.interpolate import interp1d
import gsw

# Module imports
from pyrsktools.datatypes import *
from pyrsktools.channels import *
from pyrsktools import utils

if TYPE_CHECKING:
    from pyrsktools import RSK


def calculateCTlag(
    self: RSK,
    seapressureRange: Optional[Tuple[float, float]] = None,
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "both",
    windowLength: int = 21,
) -> List[float]:
    """Calculate a conductivity lag.

    Args:
        seapressureRange (Tuple[float, float], optional): limits of the sea_pressure range used to obtain the lag.
            Specify as a two-element tuple, [seapressureMin, seapressureMax]. Default is None ((0, max(seapressure))).
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to None (all available profiles)
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".
        windowLength (int, optional): length of the filter window used for the reference salinity. Defaults to 21.

    Returns:
        List[float]: optimal lag of conductivity for each profile.  These can serve as inputs into :meth:`.RSK.alignchannel`.

    Estimates the optimal conductivity time shift relative to temperature in order to minimise salinity spiking.
    The algorithm works by computing the salinity for conductivity lags of -20 to 20 samples at 1 sample increments.
    The optimal lag is determined by constructing a high-pass filtered version of the salinity time series for every lag,
    and then computing the standard deviation of each. The optimal lag is the one that yields the smallest standard deviation.

    The seapressureRange argument allows for the possibility of estimating the lag on specific sections of the profile.
    This can be useful when unreliable measurements near the surface are found to impact the optimal lag, or when the
    profiling speed is highly variable.

    The lag output by this method is compatible with the lag input argument for :meth:`.RSK.alignchannel` when lag units is specified
    as samples in :meth:`.RSK.alignchannel`.

    Example:

    >>> rsk.calculateCTlag(seapressureRange=[0, 1.0])
    ... # Optional arguments
    ... rsk.calculateCTlag(seapressureRange=[0, 1.0], profiles=1, direction="up", windowLength=23)
    """
    self.dataexistsorerror()
    self.channelsexistorerror([Conductivity, Temperature, SeaPressure])

    if direction not in {"up", "down", "both"}:
        raise ValueError(f"Invalid direction: {direction}")

    if not self.scheduleInfo:
        raise ValueError(
            f"Method not available for RSKs with scheduling mode '{self.schedule.mode}'."
        )

    conductivity = self.data[Conductivity.longName]
    temperature = self.data[Temperature.longName]
    seaPressure = self.data[SeaPressure.longName]

    profileIndices = self.getprofilesindicessortedbycast(profiles=profiles, direction=direction)

    lag = []
    for indices in profileIndices:
        c = conductivity[indices]
        t = temperature[indices]
        sp = seaPressure[indices]

        if seapressureRange is not None:
            selectValues = np.flatnonzero(
                np.logical_and(sp >= seapressureRange[0], sp <= seapressureRange[1])
            )
            c = c[selectValues]
            t = t[selectValues]
            sp = sp[selectValues]

        lags = np.arange(-20, 21)
        runningStdDiff = np.array([], "float64")
        for l in lags:
            cShift = utils.shiftarray(c, l, "nan")
            salinity = gsw.SP_from_C(cShift, t, sp)
            salinitySmooth = utils.runavg(salinity, windowLength, "nan")
            salinityDiff = salinity - salinitySmooth
            runningStdDiff = np.append(
                runningStdDiff, np.std(salinityDiff[np.isfinite(salinityDiff)])
            )

        minlag = np.min(np.abs(lags[runningStdDiff == np.min(runningStdDiff)]))
        lag.append(minlag)

    return lag


def _checkLag(lag: npt.NDArray, castNumber: int, lagunits: str) -> npt.NDArray:
    """Checks if the lag values are intergers and either:
    one for all profiles or one for each profiles.
    """
    if not np.equal(np.fix(lag), lag).all() and lagunits == "samples":
        raise ValueError("Lag values must be integers.")

    if lagunits == "samples":
        lag = lag.astype("int64")
    if lag.size == 1 and castNumber != 1:
        lags = np.full(castNumber, lag[0])
    elif lag.size > 1 and lag.size != castNumber:
        raise ValueError("Length of lag must equal the number of profiles or be a single value.")
    else:
        lags = lag

    return lags


def alignchannel(
    self: RSK,
    channel: str,
    lag: Union[float, Collection[float]],
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "both",
    shiftfill: str = "zeroorderhold",
    lagunits: str = "samples",
) -> None:
    """Align a channel using a specified lag.

    Args:
        channel (str): longName of the channel to align (e.g. temperature)
        lag (Union[float, Collection[float]]): lag to apply to the channel, negative lag shifts the channel backwards in time (earlier),
            while a positive lag shifts the channel forward in time (later)
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to None (all available profiles)
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".
        shiftfill (str, optional): shift fill treatment of "zeroorderhold", "nan", or "mirror". Defaults to "zeroorderhold".
        lagunits (str, optional): lag units, either "samples" or "seconds". Defaults to "samples".

    Shifts a channel in time by an integer number of samples or seconds in time, specified by the argument lag.
    A negative lag shifts the channel backwards in time (earlier), while a positive lag shifts the channel forward in time (later).
    Shifting a channel is most commonly used to align conductivity to temperature to minimize salinity spiking.
    It could also be used to adjust for the time delay caused by sensors with relatively slow adjustment times (e.g., dissolved oxygen sensors).

    The shiftfill parameter describes what values will replace the shifted values. The default treatment is zeroorderhold,
    in which the first (or last) value is used to fill in the unknown data if the lag is positive (or negative). When shiftfill
    is nan, missing values are filled with NaNs. When shiftfill is mirror the edge values are mirrored to fill in the missing values.
    When shiftfill is union, all channels are truncated by lag samples. The diagram below illustrates the shiftfill options:

    .. image:: /img/RSKalignchannel.png
        :scale: 50%
        :alt: shiftfill options diagram

    Example:

    **Using RSKalignchannel to minimize salinity spiking:**

    Salinity is derived with an empirical formula that requires measurements of conductivity, temperature, and pressure.
    The conductivity, temperature, and pressure sensors all have to be aligned in time and space to achieve salinity with the
    highest possible accuracy. Poorly-aligned conductivity and temperature data will result in salinity spikes in regions where
    the temperature and salinity gradients are strong. RSK.calculateCTlag() can be used to estimate the optimal lag by minimizing
    the spikes in the salinity time series, or the lag can be estimated by calculating the transit time for water to pass from the
    conductivity sensor to the thermistor. RSK.alignchannel() can then be used to shift the conductivity channel by the desired lag,
    and then salinity needs to be recalculated using RSK.derivesalinity().

    >>> with RSK("example.rsk") as rsk:
    ...    rsk.computeprofiles(profile=range(0,9), direction="down")
    ...    # 1. Shift temperature channel of the first four profiles with the same lag value.
    ...    rsk.alignchannel(channel="temperature", lag=2, profiles=range(0,3))
    ...    # 2. Shift oxygen channel of first 4 profiles with profile-specific lags.
    ...    rsk.alignchannel(channel="dissolved_o2_concentration", lag=[2,1,-1,0], profiles=range(0,3))
    ...    # 3. Shift conductivity channel from all downcasts with optimal lag calculated with calculateCTlag().
    ...    lag = rsk.calculateCTlag()
    ...    rsk.alignchannel(channel="conductivity", lag=lag)
    """
    if shiftfill not in {"zeroorderhold", "union", "nan", "mirror"}:
        raise ValueError(f"Invalid value for argument 'shiftfill': {shiftfill}")

    if direction not in {"up", "down", "both"}:
        raise ValueError(f"Invalid direction: {direction}")

    if lagunits not in {"seconds", "samples"}:
        raise ValueError(f"Invalid value for argument 'lagunits': {lagunits}")

    self.channelsexistorerror(channel)
    self.dataexistsorerror()

    lag = utils.intoarray(lag)

    profileIndices = self.getprofilesindicessortedbycast(profiles=profiles, direction=direction)

    castNumber = len(profileIndices)

    lags = _checkLag(lag, castNumber, lagunits)

    for i, indices in enumerate(profileIndices):
        channelData = self.data[channel][indices]

        if lagunits == "seconds":
            timeLag = float(lags[i])

            # Use per-profile timestamps and duration
            timestamps_all = self.data["timestamp"].astype("float64") / 1000
            timestamps = timestamps_all[indices]

            profileTimeLength = float(timestamps[-1] - timestamps[0])
            if abs(timeLag) > profileTimeLength:
                raise ValueError("Time lag must be smaller than profile time length.")

            # Interpolate the shifted signal back onto the original profile timestamps
            shiftTime = timestamps + timeLag
            interp_func = interp1d(shiftTime, channelData, bounds_error=False, fill_value=np.nan)
            shiftChan = interp_func(timestamps)

            # Determine leading/trailing NaNs introduced by the shift (in samples)
            finite_mask = ~np.isnan(shiftChan)
            if not finite_mask.any():
                raise ValueError("Time lag too large; no overlap remains after shifting.")
            first_valid = int(np.argmax(finite_mask))
            last_valid = int(len(finite_mask) - 1 - np.argmax(finite_mask[::-1]))
            leading_nans = first_valid
            trailing_nans = len(finite_mask) - 1 - last_valid

            # Apply shiftfill behavior to edge NaNs for "seconds" path
            if shiftfill == "zeroorderhold":
                if leading_nans > 0:
                    shiftChan[:leading_nans] = shiftChan[first_valid]
                if trailing_nans > 0:
                    shiftChan[last_valid + 1 :] = shiftChan[last_valid]
            elif shiftfill == "mirror":
                if leading_nans > 0:
                    mirror_seg = shiftChan[first_valid : first_valid + leading_nans][::-1]
                    shiftChan[:leading_nans] = mirror_seg
                if trailing_nans > 0:
                    mirror_seg = shiftChan[last_valid - trailing_nans + 1 : last_valid + 1][::-1]
                    shiftChan[last_valid + 1 :] = mirror_seg
            elif shiftfill == "nan":
                pass
            elif shiftfill == "union":
                pass  # handled below via indices trimming
            else:
                raise ValueError(f"Invalid value for argument 'shiftfill': {shiftfill}")

            channelShifted = shiftChan
            # For union calculations, approximate sample trimming from introduced NaNs
            sampleLag = leading_nans if timeLag > 0 else -trailing_nans
        else:
            sampleLag = int(lags[i])
            if abs(sampleLag) > channelData.size:
                raise ValueError("Sample lag must be smaller than profile sample length.")
            shiftChan = channelData
            channelShifted = utils.shiftarray(shiftChan, sampleLag, shiftfill)

        if shiftfill == "union":
            prevIndices = indices
            if lags[i] > 0:
                indices = indices[sampleLag - 1 : -1]
                np.delete(self.data, np.setdiff1d(prevIndices, indices, assume_unique=True))
            elif lags[i] < 0:
                indices = indices[0 : len(indices) + sampleLag]
                np.delete(self.data, np.setdiff1d(prevIndices, indices, assume_unique=True))

        self.data[channel][indices[:-1]] = channelShifted[
            :-1
        ]  # skip the last point which is the start of the following cast

    self.appendlog(
        f"Channel {channel} aligned using lag(s) {','.join(map(str, lags))} and shiftfill {shiftfill}"
    )


def _setupbins(
    Y: npt.NDArray,
    binSize: npt.NDArray,
    boundary: npt.NDArray,
    direction: str,
    binByTime: bool,
    samplingPeriod: float,
) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    """Set up binArray based on the boundaries any binSize given. Boundaries
    are hard set and binSize fills the space between the boundaries in
    the same direction as the cast.

    Returns:
        Tuple[npt.NDArray, npt.NDArray, npt.NDArray]: binArray, binCenter, boundary
    """
    if binSize.size > boundary.size + 1 or (
        binSize.size < boundary.size - 1 and boundary.size == 0
    ):
        raise ValueError("Boundary must be of length of len(binSize) or len(binSize)+1")

    if binByTime:
        boundaryFloor = np.nanmin(np.nanmin(Y)) - samplingPeriod / (24.0 * 60.0 * 60.0 * 1000) / 2
        boundaryCeil = np.nanmax(np.nanmax(Y)) + samplingPeriod / (24.0 * 60.0 * 60.0 * 1000) / 2
    else:
        boundaryFloor = np.floor(np.nanmin(np.nanmin(Y)))
        boundaryCeil = np.ceil(np.nanmax(np.nanmax(Y)))

    if boundary.size == 0:
        boundary = np.array([boundaryCeil, boundaryFloor])
    elif boundary.size == binSize.size:
        boundary = np.append(boundary, [boundaryFloor if direction == "up" else boundaryCeil])
    elif boundary.size == binSize.size + 1:
        pass

    if direction == "up":
        binSize = -binSize
        boundary = boundary[np.argsort(-boundary)]
    else:
        boundary.sort()

    binArray = np.fromiter(
        (
            e
            for nregime in np.arange(boundary.size - 1)
            for e in np.arange(boundary[nregime], boundary[nregime + 1], binSize[nregime])
        ),
        dtype="float64",
    )
    binArray = np.append(binArray, binArray[-1] + binSize[-1])
    binArray = np.unique(binArray)

    binCenter = utils.lagave(binArray)[1:]

    return binArray, binCenter, boundary


def _findbinindices(
    binByValues: npt.NDArray,
    lowerboundary: npt.NDArray,
    upperboundary: npt.NDArray,
) -> npt.NDArray:
    """
    Selects the indices of the binBy channel that are within the lower
    and upper boundaries of the evaluated bin to establish which values
    from the other channel need to be averaged.
    """
    binidx = np.logical_and(binByValues >= lowerboundary, binByValues < upperboundary)

    ind = np.flatnonzero(np.diff(binidx) < 0)
    if ind.size > 0 and np.any(binByValues[ind + 1] > upperboundary):
        discardedindex = np.flatnonzero(binByValues[ind + 1] > upperboundary)[:1]
        binidx[ind[discardedindex][0] + 1 :] = 0

    return np.flatnonzero(binidx)


def binaverage(
    self: RSK,
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "down",
    binBy: str = "sea_pressure",
    binSize: Union[float, Collection[float]] = 1.0,
    boundary: Union[float, Collection[float]] = [],
) -> npt.NDArray:
    """Average the profile data by a quantized reference channel.

    Args:
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to None (all available profiles)
        direction (str, optional): cast direction of either "up" or "down". Defaults to "down".
        binBy (str, optional): reference channel that determines the samples in each bin, can be ``timestamp`` or any channel. Defaults to "sea_pressure".
        binSize (Union[float, Collection[float]], optional): size of bins in each regime. Defaults to 1.0,
            denoting 1 unit of binBy channel (e.g., 1 second when binBy is time).
        boundary (Union[float, Collection[float]], optional): first boundary crossed in the direction selected of each regime, in the same units as binBy.
            Must have len(boundary) == len(binSize) or one greater. Defaults to [] (entire range).

    Returns:
        npt.NDArray: amount of samples in each bin.

    Bins samples that fall within an interval and averages them, it is a form of data quantization.
    The bins are specified using two arguments: ``binSize`` and ``boundary``.

    1. ``binSize`` is the width (in units of ``binBy`` channel; i.e., meters if binned by depth) for each averaged bin.
       Typically the ``binSize`` should be a denominator of the space between boundaries, but if this is not the case,
       the new regime will start at the next boundary even if the last bin of the current regime is smaller than the determined binSize.
    2. ``boundary`` determines the transition from one ``binSize`` to the next.

    The cast direction establishes the bin boundaries and sizes. If the ``direction`` is up, the first boundary and binSize are
    closest to the seabed with the next boundaries following in descending order. If the ``direction`` is down, the first boundary
    and bin size are closest to the surface with the next boundaries following in descending order.

    **NOTE:** The boundary takes precedence over the bin size.
    (Ex. boundary=[5.0, 20.0], binSize = [10.0 20.0]. The bin array will be [5.0 15.0 20.0 40.0 60.0...]).
    The default  binSize is 1 dbar and the boundary is between minimum (rounded down) and maximum
    (rounded up) sea_pressure, i.e, [min(sea_pressure) max(sea_pressure)].

    A common bin system is to use 1 dbar bins from 0.5 dbar to the maximum sea_pressure value. Here is the code and a diagram:

    >>> rsk.binaverage(direction="down", binSize=1.0, boundary=0.5)

    .. figure:: /img/RSKbinaverage1.png
        :scale: 50%
        :alt: bin average common plot

        The figure above shows an original Temperature time series plotted against sea_pressure in blue.
        The dotted lines are the bin limits.
        The red dots are the averaged Temperature time series after being binned in 1dbar bins.
        The temperature values are centred in the middle of the bin (between the dotted lines) and are an average
        of all the values in the original time series that fall within the determined interval.

    The diagram and code below describe the bin array for a more complex binning with different regimes throughout the water column:

    >>> samplesinbin = rsk.binaverage(direction="down", binBy="Depth", binSize=[10.0, 50.0], boundary=[10.0, 50.0, 200.0])

    .. figure:: /img/RSKbinaverage2.png
        :scale: 50%
        :alt: bin average complex plot

        Note the discarded measurements in the image above the 50m dashed line. Once the samples have started in the next bin,
        the previous bin closes, and further samples in that bin are discarded.

    The diagram and code below give an example when the average is done against time (i.e. binBy = "timestamp"),
    with the unit in seconds. Here we average for every ten minutes (i.e. 600 seconds).

    >>> samplesinbin = rsk.binaverage(binBy="time", binSize=600.0)

    .. figure:: /img/RSKbinaverage3.png
        :scale: 50%
        :alt: bin average time plot

        The figure above shows an original Temperature time series plotted against Time in blue.
        The dotted lines are the bin limits.
        The red dots are the averaged Temperature time series after being binned in 10 minutes bins.
        The temperature values are centred in the middle of the bin (between the dotted lines) and are
        an average of all the values in the original time series that fall within the determined interval.
    """
    self.dataexistsorerror()
    if binBy.lower().startswith("time"):
        binBy = "timestamp"
    self.channelsexistorerror([binBy])

    if direction not in ("up", "down"):
        raise ValueError(f"Invalid direction: {direction}")

    if not self.scheduleInfo:
        raise ValueError(
            f"Method not available for RSKs with scheduling mode '{self.schedule.mode}'."
        )

    binSize = utils.intoarray(binSize)
    boundary = utils.intoarray(boundary)

    if not self.getregionsbytypes([RegionCast, RegionProfile]):
        profileIndices = self.getdataseriesindices()
    else:
        profileIndices = self.getprofilesindices(profiles, direction)

    maxlength = max([len(indices) for indices in profileIndices])
    samplingPeriod = self.scheduleInfo.samplingperiod()
    numberOfProfiles = len(profileIndices)

    binByTime: bool = binBy == "timestamp"
    Y = np.full((maxlength, numberOfProfiles), np.nan, dtype="float64")

    if binByTime:
        binSize = binSize / 24.0 * 60.0 * 60.0 * 1000 / 150
    else:
        binByCol = [i for i, name in enumerate(self.channelNames) if name == binBy][0]

    for i in range(numberOfProfiles):
        ref = self.data[binBy][profileIndices[i]]
        Y[0 : ref.size, i] = ref - ref[0] if binByTime else ref

    binArray, binCenter, boundary = _setupbins(
        Y, binSize, boundary, direction, binByTime, samplingPeriod
    )

    timedeltas = self.data["timestamp"].astype("timedelta64[ms]")
    dtype = self.data.dtype  # Cache the full dtype to recreate self.data again later
    self.data = rfn.drop_fields(self.data, "timestamp")  # Drop to avoid errors during averaging
    self.data = rfn.structured_to_unstructured(self.data)  # Turn into a 2-D NDArray
    binnedSize = numberOfProfiles * (binArray.size - 1)
    samplesinbin = np.zeros(binnedSize, "uint32")

    def datagenerator() -> Iterator[Tuple[Any, ...]]:
        k = 0
        nullValues = np.full(self.data.shape[1], np.nan)

        for i in np.arange(numberOfProfiles):
            pTimedeltas = timedeltas[profileIndices[i]]
            pData = self.data[profileIndices[i]]

            for j in np.arange(binArray.size - 1):
                binIndices = _findbinindices(Y[:, i], binArray[j], binArray[j + 1])

                if binIndices.size > 0:
                    samplesinbin[k] = binIndices.size
                    timestamp = np.mean(pTimedeltas[binIndices]).astype("datetime64[ms]")
                    binnedValues = np.nanmean(pData[binIndices, :], axis=0)
                else:
                    timestamp = pTimedeltas[0].astype("datetime64[ms]")
                    binnedValues = nullValues

                if not binByTime:
                    binnedValues[binByCol] = binCenter[j]

                yield (timestamp, *binnedValues)
                k += 1

    self.data = np.fromiter(datagenerator(), dtype, binnedSize)

    unit = (
        "timestamp"
        if binBy == "timestamp"
        else [ch.units for ch in self.channels if ch.longName == binBy][0]
    )
    self.appendlog(
        f"Binned with respect to {binBy} using {boundary} boundaries with {binSize} {unit} bin size."
    )

    return samplesinbin


def _correcthold(
    channelData: npt.NDArray, timestamps: npt.NDArray, action: str
) -> Tuple[npt.NDArray, npt.NDArray]:
    """
    Replaces zero-order hold values with either a NaN or interpolated
    value using the neighbouring points.
    """
    correctedChannelData = channelData
    needCorrectionIndices = np.flatnonzero(np.diff(channelData) == 0) + 1
    # if two elements are the same in an array, np.diff returns the index of the first element, so +1 to get the index of the second element

    if needCorrectionIndices.size > 0 and np.any(channelData):
        if action == "interp":
            good = np.flatnonzero(~np.isin(np.arange(timestamps.size), needCorrectionIndices))
            timestamps = timestamps.astype("float64")
            correctedChannelData[needCorrectionIndices] = interp1d(
                timestamps[good], channelData[good], bounds_error=False
            )(timestamps[needCorrectionIndices])
        elif action == "nan":
            correctedChannelData[needCorrectionIndices] = np.nan

    return correctedChannelData, needCorrectionIndices


def correcthold(
    self: RSK,
    channels: Union[str, Collection[str]] = [],
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "both",
    action: str = "nan",
) -> dict:
    """Replace zero-order hold points with interpolated values or NaN.

    Args:
        channels (Union[str, Collection[str]], optional): longname of channel to correct the zero-order hold (e.g., temperature, salinity, etc).
            Defaults to [] (all available channels).
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to [] (all available profiles).
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".
        action (str, optional): action to perform on a hold point. Given "nan", hold points are replaced with NaN.
            Another option is "interp", whereby hold points are replaced with values calculated by linearly
            interpolating from the neighbouring points. Defaults to "nan".

    Returns:
        dict: a reference dict with values giving the index of the corrected hold points; each returned key-value pair
            has the channel name as the key and an array of indices relating to the respective channel as the value.

    The analogue-to-digital (A2D) converter on RBR instruments must recalibrate periodically. In the time it takes for
    the calibration to finish, one or more samples are missed. The onboard firmware fills the missed sample with the same
    data measured during the previous sample, a simple technique called a zero-order hold.

    This method identifies zero-hold points by looking for where consecutive differences for each channel are equal to zero
    and replaces them with an interpolated value or a NaN.

    An example of where zero-order holds are important is when computing the vertical profiling rate from pressure.
    Zero-order hold points produce spikes in the profiling rate at regular intervals, which can cause the points to
    be flagged by :meth:`.RSK.removeloops`.

    Example:

    >>> holdpts = rsk.correcthold()

    .. figure:: /img/RSKcorrecthold.png
        :scale: 50%
        :alt: correct hold plot

        The green squares indicate the original data.
        The red crossings are the interpolated data after correcting zero-order holds.
    """
    if direction not in {"up", "down", "both"}:
        raise ValueError(f"Invalid direction: {direction}")

    if action not in {"nan", "interp"}:
        raise ValueError(f"Unrecognized value for argument 'action': {action}")

    self.dataexistsorerror()
    self.channelsexistorerror(channels)

    profileIndices = self.getprofilesindicessortedbycast(profiles=profiles, direction=direction)

    channelNames, _ = self.getchannelnamesandunits(channels)

    holdpts = {}

    for channelName in channelNames:
        pts = np.array([], dtype="int64")
        for indices in profileIndices:
            correctedChannelData, correctedIndices = _correcthold(
                self.data[channelName][indices],
                self.data["timestamp"][indices],
                action,
            )

            if correctedIndices.size > 0:
                self.data[channelName][indices[:-1]] = correctedChannelData[:-1]
                pts = np.append(pts, np.array(indices, "int64")[correctedIndices])

        if pts.size > 0:
            holdpts[channelName] = pts

    self.appendlog(
        f"Zero-order hold corrected for channel(s) {', '.join(channelNames)}. Hold points were treated with {action}."
    )
    return holdpts


def _despike(
    inArray: npt.NDArray,
    time: npt.NDArray,
    threshold: int = 2,
    windowLength: int = 3,
    action: str = "nan",
) -> Tuple[npt.NDArray, npt.NDArray]:
    """ " Replaces the values that are > threshold*standard deviation away from
    the residual between the original time series and the running median
    with the median, a NaN or interpolated value using the non-spike
    values. The output is the input series with spikes fixed and dict is the
    index of the spikes.
    """

    outArray = inArray
    refArray = utils.runmed(inArray, windowLength)
    dx = inArray - refArray
    sd = dx.std(axis=0)  # to do need to exclu infinity in dx??
    despikedIndices = np.flatnonzero(abs(dx) > (threshold * sd))

    if action == "replace":
        outArray[despikedIndices] = refArray[despikedIndices]
    elif action == "nan":
        outArray[despikedIndices] = np.nan
    elif action == "interp":
        good = np.flatnonzero(abs(dx) <= (threshold * sd))
        time = time.astype("float64")
        outArray[despikedIndices] = np.interp(time[despikedIndices], time[good], inArray[good])
    else:
        raise ValueError(f"Invalid action to perform on a spike: {action}")

    return outArray, despikedIndices


def despike(
    self: RSK,
    channels: str,
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "both",
    threshold: int = 2,
    windowLength: int = 3,
    action: str = "nan",
) -> dict:
    """Despike a time series on a specified channel.

    Args:
        channels (str): longname of channel to despike (e.g., temperature, or salinity, etc).
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to [] (all available profiles).
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".
        threshold (int, optional): amount of standard deviations to use for the spike criterion. Defaults to 2.
        windowLength (int, optional): total size of the filter window. Must be odd. Defaults to 3.
        action (str, optional):  action to perform on a spike. Given "nan", spikes are replaced with NaN. Other
            options are "replace", whereby spikes are replaced with the corresponding reference value, and "interp"
            whereby spikes are replaced with values calculated by linearly interpolating from the neighbouring points.
            Defaults to "nan".

    Returns:
        dict: dict with values giving the index of the spikes.

    Removes or replaces spikes in the data from the ``channel`` specified.  The algorithm used here is to discard points
    that lie outside of a ``threshold``.  The data are smoothed by a median filter of length ``windowLength`` to produce a "reference"
    time series. Residuals are formed by subtracting the reference time series from the original time series. Residuals that fall
    outside of a ``threshold``, specified as the number of standard deviations, where the standard deviation is computed from the residuals,
    are flagged for removal or replacement.

    The default behaviour is to replace the flagged values with NaNs. Flagged values can also be replaced with reference values, or
    replaced with values linearly interpolated from neighbouring "good" values.

    Example:

    >>> spikes = rsk.despike(channel="Temperature", profiles=range(0, 4), direction="down",
            threshold=4.0, windowLength=11, action="nan")

    .. figure:: /img/RSKdespike.png
        :scale: 50%
        :alt: despike plot

        The red circles indicate the samples in the blue time series that spike.
        The green lines are the limits determined by the ``threshold`` parameter.
        The black time series is, as referred to above, the reference series. It is the filtered original time series.
    """

    self.dataexistsorerror()
    self.channelsexistorerror(channels)

    if action not in ("replace", "interp", "nan"):
        raise ValueError(f"Invalid action to perform on a spike: {action}")

    if direction not in ("up", "down", "both"):
        raise ValueError(f"Invalid direction: {direction}")

    channelNames, _ = self.getchannelnamesandunits(channels)

    if not self.getregionsbytypes([RegionCast, RegionProfile]):
        dataIndices = self.getdataseriesindices()
    else:
        dataIndices = self.getprofilesindicessortedbycast(profiles=profiles, direction=direction)

    spikepts = {}

    for channelName in channelNames:
        pts = np.array([], dtype="int64")
        for indices in dataIndices:
            despikedData, despikedIndices = _despike(
                self.data[channelName][indices],
                self.data["timestamp"][indices],
                threshold,
                windowLength,
                action,
            )

            if despikedIndices.size > 0:
                self.data[channelName][indices[:-1]] = despikedData[:-1]
                pts = np.append(pts, np.array(indices, "int64")[despikedIndices])

        if pts.size > 0:
            spikepts[channelName] = np.unique(pts)

    self.appendlog(
        f"Despiked for channel(s) {', '.join(channelName)}. Spike points were treated with {action}."
    )

    return spikepts


def smooth(
    self: RSK,
    channels: Union[str, Collection[str]],
    filter: str = "boxcar",
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "both",
    windowLength: int = 3,
) -> None:
    """Apply a low pass filter on the specified channel(s).

    Args:
        channels (Union[str, Collection[str]]): longname of channel to filter. Can be a single channel,
            or a list of multiple channels.
        filter (str, optional): the weighting function, "boxcar", "triangle", or "median". Defaults to "boxcar".
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to [] (all available profiles).
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".
        windowLength (int, optional): the total size of the filter window. Must be odd. Defaults to 3.

    Applies a low-pass filter to a specified channel or multiple channels with a running average or median.
    The sample being evaluated is always in the centre of the filtering window to avoid phase distortion.
    Edge effects are handled by mirroring the original time series.

    The ``windowLength`` argument determines the degree of smoothing. If ``windowLength`` = 5; the filter is composed of
    two samples from either side of the evaluated sample and the sample itself.  ``windowLength`` must be odd to centre
    the average value within the window.

    The median filter is less sensitive to extremes (best for spike removal), whereas the boxcar and triangle filters
    are more effective at noise reduction and smoothing.

    Example:

    >>> rsk.smooth(channels=["temperature", "salinity"], windowLength=17)

    The figures below demonstrate the effect of the different available filters:

    .. figure:: /img/RSKsmooth1.png
        :scale: 50%
        :alt: first smooth plot

        The effect of the various low-pass filters implemented by :meth:`RSKsmooth` on a step function.
        Note that in this case, the median filter leaves the original step signal unchanged.

    .. figure:: /img/RSKsmooth2.png
        :scale: 50%
        :alt: second smooth plot

        Example of the effect of various low-pass filters on a time series.
    """
    self.dataexistsorerror()
    self.channelsexistorerror(channels)
    channelNames, _ = self.getchannelnamesandunits(channels)

    if direction not in ("up", "down", "both"):
        raise ValueError(f"Invalid direction: {direction}")

    if not self.getregionsbytypes([RegionCast, RegionProfile]):
        dataIndices = self.getdataseriesindices()
    else:
        dataIndices = self.getprofilesindicessortedbycast(profiles=profiles, direction=direction)

    for i in range(len(channelNames)):
        for indices in dataIndices:
            lastValue = self.data[channelNames[i]][indices[-1]]
            if filter == "boxcar":
                self.data[channelNames[i]][indices] = utils.runavg(
                    self.data[channelNames[i]][indices], windowLength
                )
                if len(dataIndices) > 1:
                    self.data[channelNames[i]][indices[-1]] = lastValue
            elif filter == "median":
                self.data[channelNames[i]][indices] = utils.runmed(
                    self.data[channelNames[i]][indices], windowLength
                )
                if len(dataIndices) > 1:
                    self.data[channelNames[i]][indices[-1]] = lastValue
            elif filter == "triangle":
                self.data[channelNames[i]][indices] = utils.runtriang(
                    self.data[channelNames[i]][indices], windowLength
                )
                if len(dataIndices) > 1:
                    self.data[channelNames[i]][indices[-1]] = lastValue
            else:
                raise ValueError(f"Invalid filter method name: {filter}")

    self.appendlog(
        f"Smooth for channel(s) {', '.join(channelNames[i])} with the method of {filter}."
    )


def removeloops(
    self: RSK,
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "both",
    threshold: float = 0.25,
) -> List[int]:
    """Remove data with a profiling rate less than a threshold and with reversed pressure (loops).

    Args:
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to [] (all available profiles).
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".
        threshold (float, optional): minimum speed at which the profile must be taken. Defaults to 0.25 m/s.

    Returns:
        dict: dict with values giving the index of the samples that are flagged

    Flags and replaces pressure reversals or profiling slowdowns with NaNs in the data
    field of this RSK instance and returns the index of these samples. Variations in profiling rate are caused by,
    for example, profiling from a vessel in rough seas with a taut wire, or by lowering a CTD hand over hand.
    If the ship heave is large enough, the CTD can momentarily change direction even though the line is paying out,
    causing a "loop" in the velocity profile.  Under these circumstances the data can be contaminated because
    the CTD samples its own wake; this method is designed to minimise the impact of such situations.

    First, this method low-pass filters the depth channel with a 3-point running average boxcar window to reduce
    the effect of noise. Second, it calculates the velocity using a simple two-point finite difference scheme and
    interpolates the velocity back onto the original timestamps. Lastly, it flags samples associated with a profiling
    velocity below the ``threshold`` value and replaces the corresponding points in all channels with NaN.
    Additionally, any data points with reversed pressure (i.e. decreasing pressure during downcast
    or increasing pressure during upcast) will be flagged as well, to ensure that data with above threshold
    velocity in a reversed loop are removed.

    The convention is for downcasts to have positive profiling velocity. This method automatically accounts for the upcast velocity sign change.

    **NOTE**:

    The input RSK must contain a ``depth`` channel. See :meth:`RSK.derivedepth()`.

    While the ``depth`` channel is filtered by a 3-point moving average in order to calculate the profiling velocity,
    the ``depth`` channel in the :obj:`RSK.data` is not altered.

    Example:

    >>> loops = rsk.removeloops(direction= "down", threshold= 0.1)

    .. figure:: /img/RSKremoveloops.png
        :scale: 50%
        :alt: remove loops plot

        Shown here are profiles of temperature (left panel) and profiling velocity (right panel).
        The red dash-dot line illustrates the ``threshold`` velocity; set in this example to 0.1 m/s.
        The temperature readings for which the profiling velocity was below 0.1 m/s are illustrated by the red dots.
    """
    self.dataexistsorerror()
    self.channelsexistorerror([SeaPressure])
    self.channelsexistorerror([Depth])
    self.channelsexistorerror([Velocity])

    if direction not in ("up", "down", "both"):
        raise ValueError(f"Invalid direction: {direction}")

    if not self.getregionsbytypes([RegionCast, RegionProfile]):
        raise ValueError(
            f"There is no profiles in .rsk file. RSKremoveloops only applies to profile data."
        )
    else:
        profileIndices = self.getprofilesindicessortedbycast(profiles=profiles, direction=direction)

    flagIndices = np.array([], dtype="int64")
    for i, indices in enumerate(profileIndices):
        indices = np.array(indices)
        depth = utils.runavg(self.data[Depth.longName][indices], 3, "nan")
        velocity = self.data[Velocity.longName][indices]
        # acc = utils.calculatevelocity(Velocity, time) # a hidden argument

        if utils.getcastdirection(depth, "up"):
            vIndices = velocity > -threshold  # |  (acc > -accelerationThreshold)
            cm = np.minimum.accumulate(depth)
            dIndices = (depth - cm) > 0
            fIndices = indices[np.logical_or(dIndices, vIndices)]
        else:
            vIndices = velocity < threshold  # | (acc < accelerationThreshold)
            cm = np.maximum.accumulate(depth)
            dIndices = (depth - cm) < 0
            fIndices = indices[np.logical_or(dIndices, vIndices)]

        if fIndices.size > 0:
            if flagIndices.size == 0:
                flagIndices = np.append(flagIndices, fIndices)
            else:
                if flagIndices[-1] != fIndices[1]:
                    flagIndices = np.append(flagIndices, fIndices)
                else:
                    flagIndices = np.append(flagIndices[:-1], fIndices)

    flagChannels = [c for c in self.channelNames if c not in {"Depth", "Pressure", "Sea Pressure"}]

    for chan in flagChannels:
        self.data[chan][flagIndices] = np.nan

    self.appendlog(f"Remove loops with the threshold of {threshold} m/s.")

    return list(flagIndices)


def trim(
    self: RSK,
    reference: str,
    range: Tuple[Union[np.datetime64, int], Union[np.datetime64, int]],
    channels: Union[str, Collection[str]] = [],
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "both",
    action: str = "nan",
) -> List[int]:
    """Remove or replace values that fall in a certain range.

    Args:
        reference (str): channel that determines which samples will be in the range and trimmed.
            To trim according to time, use "time", or, to trim by index, choose "index".
        range (Tuple[Union[np.datetime64, int], Union[np.datetime64, int]]):
            A 2-element tuple of minimum and maximum values.
            The samples in "reference" that fall within the range (including the edges)
            will be trimmed. If "reference" is "time", then each range element must be a NumPy datetime64 object.
        channels (Union[str, Collection[str]]): apply the flag to specified channels. When action is set to
            ``remove``, specifying channel will not work. Defaults to [] (all available channels).
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to [] (all available profiles).
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".
        action (str, optional): action to apply to the flagged values.
            Can be "nan", "remove", or "interp". Defaults to "nan".

    Returns:
        List[int]: a list containing the indices of the trimmed samples.

    The ``reference`` argument could be a channel name (e.g. sea_pressure), ``time``, or ``index``.
    The ``range`` argument is a 2-element vector of minimum and maximum values.
    The samples in ``reference`` that fall within the range (including the edge) will be trimmed.
    When ``reference`` is ``time``, each range element must be a np.datetime64 object.
    When ``reference`` is ``index``, each range element must be an integer number.

    This method provides three options to deal with flagged data, which are:

    1. ``nan`` - replace flagged samples with NaN
    2. ``remove`` - remove flagged samples
    3. ``interp`` - replace flagged samples with interpolated values by neighbouring points.

    Example:

    >>> # Replace data acquired during a shallow surface soak with NaN
    ... rsk.trim(reference="sea_pressure", range=[-1.0, 1.0], action="NaN")
    ...
    ... # Remove data before 2022-01-01
    ... rsk.trim(reference="time", range=[np.datetime64("0"), np.datetime64("2022-01-01")], action="remove")
    """
    if direction not in {"up", "down", "both"}:
        raise ValueError(f"Invalid direction: {direction}")

    if action not in {"nan", "remove", "interp"}:
        raise ValueError(f"Unrecognized value for argument 'action': {action}")

    # If they didn't use time or index as a reference, assume they used
    # a channel name and check for its existence.
    if reference not in {"time", "index"}:
        self.getchannelnamesandunits(reference)

    self.dataexistsorerror()
    self.channelsexistorerror(channels)

    # If reference is time, ensure times are in ms format to match self.data timestamps
    if reference == "time":
        if not (isinstance(range[0], np.datetime64) and isinstance(range[0], np.datetime64)):
            raise TypeError(
                "Each range tuple element must be a NumPy datetime64 object when reference is time."
            )
        range = (range[0].astype("datetime64[ms]"), range[1].astype("datetime64[ms]"))  # type: ignore

    if action == "remove" and channels != []:
        raise TypeError("Cannot specify channels with action 'remove'.")

    profileIndices = self.getprofilesindices(profiles, direction)

    channelNames, _ = self.getchannelnamesandunits(channels)

    if action == "interp":
        timestamp = self.data["timestamp"].astype("float64")

    trimmedIndices = set()
    for indices in profileIndices:
        indices = np.array(indices)
        if reference == "index":
            refData = indices
        elif reference == "time":
            refData = self.data["timestamp"][indices]
        else:
            refData = self.data[reference][indices]

        # Find indices
        trimIndices = indices[np.logical_and(refData >= range[0], refData <= range[1])]
        nonTrimIndices = indices[np.logical_or(refData < range[0], refData > range[1])]

        if trimIndices.size > 0:
            if action == "interp":
                if nonTrimIndices.size > 0:
                    for channelName in channelNames:
                        self.data[channelName][trimIndices] = interp1d(
                            timestamp[nonTrimIndices],
                            self.data[channelName][nonTrimIndices],
                            bounds_error=False,
                        )(timestamp[trimIndices])
            else:
                for channelName in channelNames:
                    self.data[channelName][trimIndices] = np.nan

            trimmedIndices.update(trimIndices.tolist())

    if action == "remove":
        self.data = np.delete(self.data, np.array(list(trimmedIndices), dtype=int))

    return list(trimmedIndices)


def _correctTM(
    temperature: npt.NDArray, timestamp: npt.NDArray, a: float, b: float, gamma: float
) -> npt.NDArray:
    indices = np.isfinite(temperature)
    timestamp = timestamp.astype("float64")  # Convert to seconds
    interpTemp = interp1d(
        timestamp[indices],
        temperature[indices],
        kind="linear",
        fill_value="extrapolate",
    )(timestamp)

    conductivityCorrection = np.zeros(temperature.size)
    for i in np.arange(1, temperature.size):
        conductivityCorrection[i] = -b * conductivityCorrection[i - 1] + gamma * a * (
            interpTemp[i] - interpTemp[i - 1]
        )
    conductivityCorrection[~indices] = np.nan

    return conductivityCorrection


def correctTM(
    self: RSK,
    alpha: float,
    beta: float,
    gamma: float = 1.0,
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "both",
) -> None:
    """Apply a thermal mass correction to conductivity using the model of Lueck and Picklo (1990).

     Args:
        alpha (float):  volume-weighted magnitude of the initial fluid thermal anomaly.
        beta (float): inverse relaxation time of the adjustment.
        gamma (float, optional):  temperature coefficient of conductivity (dC/dT). Defaults to 1.0.
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to [] (all available profiles).
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".

    Applies the algorithm developed by Lueck and Picklo (1990) to minimize the effect of conductivity cell
    thermal mass on measured conductivity. Conductivity cells exchange heat with the water as they travel through
    temperature gradients. The heat transfer changes the water temperature and hence the measured conductivity.
    This effect will impact the derived salinity and density in the form of sharp spikes and even a bias under certain conditions.

    Example:

    >>> rsk.correctTM(alpha=0.04, beta=0.1)

    References:
        * Lueck, R. G., 1990: Thermal inertia of conductivity cells: Theory. J. Atmos. Oceanic Technol., 7, pp. 741 - 755. `<https://doi.org/10.1175/1520-0426(1990)007\<0741:TIOCCT\>2.0.CO;2>`_
        * Lueck, R. G. and J. J. Picklo, 1990: Thermal inertia of conductivity cells: Observations with a Sea-Bird cell. J. Atmos. Oceanic Technol., 7, pp. 756 - 768. `<https://doi.org/10.1175/1520-0426(1990)007\<0756:TIOCCO\>2.0.CO;2>`_
    """
    if direction not in {"up", "down", "both"}:
        raise ValueError(f"Invalid direction: {direction}")

    self.dataexistsorerror()
    self.channelsexistorerror([Temperature, Conductivity])

    fs = np.round(1 / self.scheduleInfo.samplingperiod())
    a = 4 * fs / 2 * alpha / beta * 1 / (1 + 4 * fs / 2 / beta)
    b = 1 - 2 * a / alpha

    timestamp = self.data["timestamp"]
    temperature = self.data[Temperature.longName]
    conductivity = self.data[Conductivity.longName]

    profileIndices = self.getprofilesindicessortedbycast(profiles=profiles, direction=direction)

    for indices in profileIndices:
        correction = _correctTM(temperature[indices], timestamp[indices], a, b, gamma)
        conductivity[indices[:-1]] += correction[:-1]

    self.appendlog(
        f"Thermal mass correction applied to conductivity with alpha = {alpha}, beta = {beta} s^-1, and gamma = {gamma}."
    )


def _correcttau(
    channelData: npt.NDArray, timestamp: npt.NDArray, r: float, s: float
) -> npt.NDArray:
    indices = np.isfinite(channelData)
    timestamp = timestamp.astype("float64")
    interpData = interp1d(
        timestamp[indices],
        channelData[indices],
        kind="linear",
        fill_value="extrapolate",
    )(timestamp)

    correctedData = np.full(channelData.size, np.nan)
    idd = indices.all()
    correctedData[0] = channelData[0]

    for i in np.arange(1, correctedData.size):
        correctedData[i] = ((1.0 - s) / (1.0 - r)) * (
            interpData[i] - r * interpData[i - 1]
        ) + s * correctedData[i - 1]

    correctedData[~indices] = np.nan
    return correctedData


def correcttau(
    self: RSK,
    channel: str,
    tauResponse: int,
    tauSmooth: int = 0,
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "both",
) -> None:
    """Apply tau correction and smoothing (optional) algorithm from Fozdar et al. (1985).

    Args:
        channel (str): longName of channel to apply tau correction (e.g., "Temperature", "Dissolved O2").
        tauResponse (int): sensor time constant of the channel in seconds.
        tauSmooth (int, optional): smoothing time scale in seconds. Defaults to 0.
        profiles (Union[int, Collection[int]], optional): profile number(s). Defaults to [] (all available profiles).
        direction (str, optional): cast direction of either "up", "down", or "both". Defaults to "both".

    Sensors require a finite time to reach equilibrium with the ambient environment under variable conditions.
    The adjustment process alters both the magnitude and phase of the true signal.
    The time response of a sensor is often characterized by a time constant, which is defined as the time it takes
    for the measured signal to reach 63.2% of the difference between the initial and final values after a step change.

    This method applies the Fozdar et al. (1985; Eq. 3.15) algorithm to correct the phase and response of a measured
    signal to more accurately represent the true signal. The Fozdar expression is different from others because it
    includes a smoothing time constant to reduce the noise added by sharpening algorithms. When the smoothing time
    constant is set to zero (the default value for :meth:`RSK.correcttau`), the Fozdar algorithm reduces to the discrete form
    of a commonly-used model to correct for the thermal lag of a thermistor:

    .. math:: T = T_m + τ\\frac{ dT_m  }{ dt }

    where :math:`T_m` is the measured temperature, :math:`T` is the true temperature,
    and `τ` is the thermistor time constant (Fofonoff et al., 1974).

    Below is an example showing how the Fozdar algorithm, with no smoothing time constant, enhances the response of a
    RBRcoda T.ODO|standard (`τ` = 8s) data taken during a CTD profile.
    The CTD had an RBRcoda T.ODO|fast (`τ` = 1s) to serve as a reference.
    The graph shows that the Fozdar algorithm, when applied to data from the standard response optode, does a good job
    of reconstructing the true dissolved oxygen profile by recovering both the phase and amplitude lost by its relatively
    long time constant. The standard deviation of the difference between standard and fast optode is greatly reduced.

    .. figure:: /img/RSKcorrecttau.png
        :scale: 25%
        :alt: correct tau plot

        Dissolved O2 from T.ODO fast, T.ODO standard and T.ODO standard after tau correction (left panel)
        Dissolved O2 differences between T.ODO standard with and without correction and T.ODO fast (middle panel)
        Histogram of the differences (right panel).

    The use of the Fozdar algorithm on RBR optode data is currently being studied at RBR, and more tests are needed
    to determine the optimal value for parameter ``tauSmooth`` on sensors with different time constants. RBR is also planning
    to evaluate the use of other algorithms that have been tested on oxygen optode data, such as the "bilinear" filter
    (Bittig et al., 2014).

    Example:

    >>> rsk.correcttau(channel="dissolved_o2_saturation", tauResponse=8, direction="down", profiles=1)

    References:
        * Bittig, Henry C., Fiedler, Björn, Scholz, Roland, Krahmann, Gerd, Körtzinger, Arne, ( 2014), Time response of oxygen optodes on profiling platforms and its dependence on flow speed and temperature, Limnology and Oceanography: Methods, 12, doi: `<https://doi.org/10.4319/lom.2014.12.617>`_.
        * Fofonoff, N. P., S. P. Hayes, and R. C. Millard, 1974: WHOI/Brown CTD microprofiler: Methods of calibration and data handling. Woods Hole Oceanographic Institution Tech. Rep., 72 pp., `<https://doi.org/10.1575/1912/647>`_.
        * Fozdar, F.M., G.J. Parkar, and J. Imberger, 1985: Matching Temperature and Conductivity Sensor Response Characteristics. J. Phys. Oceanogr., 15, 1557-1569, `<https://doi.org/10.1175/1520-0485(1985)015\<1557:MTACSR\>2.0.CO;2>`_.
    """
    if direction not in {"up", "down", "both"}:
        raise ValueError(f"Invalid direction: {direction}")

    self.dataexistsorerror()
    self.channelsexistorerror([channel])

    timestamp = self.data["timestamp"]
    channelData = self.data[channel]

    profileIndices = self.getprofilesindicessortedbycast(profiles=profiles, direction=direction)

    dt = self.scheduleInfo.samplingperiod()
    with np.errstate(divide="ignore"):
        r = np.exp(np.true_divide(-dt, tauResponse))
        s = np.exp(np.true_divide(-dt, tauSmooth))

    for i, indices in enumerate(profileIndices):
        lastValue = self.data[channel][indices[-1]]

        self.data[channel][indices] = _correcttau(channelData[indices], timestamp[indices], r, s)
        self.data[channel][indices[-1]] = lastValue

    self.appendlog(
        f"Channel {channel} tau-corrected using tau response time of {tauResponse} sec and tau smooth time of {tauSmooth}."
    )


def generate2D(
    self: RSK,
    channels: Union[str, Collection[str]] = [],
    profiles: Optional[Union[int, Collection[int]]] = [],
    direction: str = "down",
    reference: str = "sea_pressure",
) -> Image:
    """Generate data for 2D plot by RSK.images().

    Args:
        channels (Union[str, Collection[str]], optional): longName of channel(s) to generate data. Defaults to [] (all available channels).
        profiles (Union[int, Collection[int]] , optional): profile numbers to use. Defaults to [] (all available profiles).
        direction (str, optional): cast direction of either "up" or "down". Defaults to "down".
        reference (str, optional): channel that will be used as y dimension. Defaults to "sea_pressure".

    Arranges a series of profiles from selected channels into in a 3D matrix.
    The matrix has dimensions MxNxP, where M is the number of depth or pressure levels, N is the number of profiles,
    and P is the number of channels. Arranged in this way, the matrices are useful for analysis and for 2D visualization
    (:meth:`RSK.images()` uses :meth:`RSK.generate2D()`). It may be particularly useful for users wishing to visualize multidimensional
    data without using :meth:`RSK.images()`. Each profile must be placed on a common reference grid before using this method (see :meth:`RSK.binaverage()`).

    Example:

    >>> rsk.generate2D(channels=["temperature", "conductivity"], direction="down")
    """
    self.dataexistsorerror()
    self.channelsexistorerror(channels)
    self.channelsexistorerror(reference)

    if direction not in ("up", "down"):
        raise ValueError(f"Invalid direction: {direction}")

    referenceChannels = {reference, SeaPressure.longName, Pressure.longName, Depth.longName}
    channelNames, channelUnits = self.getchannelnamesandunits(channels, exclude=referenceChannels)

    if len(channelNames) == 0:
        raise ValueError(
            f"All channels to plot exist within the set of reference channels ({', '.join(referenceChannels)})."
        )

    profileIndices = self.getprofilesindices(profiles, direction)
    Y = self.data[reference]

    for i in range(len(profileIndices) - 1):
        if Y[profileIndices[i]].size == Y[profileIndices[i + 1]].size:
            binCenter = Y[profileIndices[i]]
        else:
            raise ValueError(
                "The reference channel data of all the selected profiles must be identical. "
                "Use RSK.binaverage() for the selected cast direction."
            )

    image = Image(
        x=np.fromiter(
            (np.min(self.data["timestamp"][indices]) for indices in profileIndices),
            "datetime64[ms]",
            len(profileIndices),
        ),
        y=binCenter,
        channelNames=channelNames,
        channelUnits=channelUnits,
        profiles=profiles,
        direction=direction,
        data=np.full((binCenter.size, len(profileIndices), len(channelNames)), np.nan),
        reference=reference,
        referenceUnit=[c.units for c in self.channels if c.longName == reference][0],
    )

    for i, channelName in enumerate(image.channelNames):
        binValues = np.full((binCenter.size, len(profileIndices)), np.nan)
        for j, indices in enumerate(profileIndices):
            binValues[:, j] = self.data[channelName][indices]
        image.data[:, :, i] = binValues

    return image


def centrebursttimestamp(self: RSK) -> None:
    """Modify wave/BPR file timestamp in the data field from beginning to middle of the burst.

    For wave or BPR loggers, Ruskin stores the raw high-frequency values in the ``burstData`` field.
    The data field is composed of one sample for each burst with a timestamp set to be the first value
    of each burst period; the sample is the average of the values during the corresponding burst.
    For users' convenience, this method modifies the timestamp from the beginning of each burst to the middle of it.

    **NOTE**: This method examines if the rsk file contains ``burstData`` field, if not, it will not proceed.

    .. figure:: /img/RSKcentrebursttimestamp.png
        :scale: 30%
        :alt: centre burst timestamp plot

        In the figure above, the blue line is the values in the ``burstdata`` field and the red dots are the values in
        the ``data`` field (i.e. the average of each burst period). The top panel shows the timestamp at beginning of the burst, while
        the bottom panel shows the timestamp in the middle of the burst after the application of this method.

    Example:

    >>> rsk.centrebursttimestamp()
    """
    self.dataexistsorerror()

    if not isinstance(self.scheduleInfo, WaveInfo):
        raise TypeError(f"This method only applies to wave data.")

    dt = (self.scheduleInfo.samplingCount / 2) * self.scheduleInfo.samplingperiod()
    self.data["timestamp"] = (self.data["timestamp"].astype("float64") + (dt * 1000)).astype(
        "datetime64[ms]"
    )

    self.appendlog(f"Timestamp for wave data centered/shifted by {dt} seconds.")
