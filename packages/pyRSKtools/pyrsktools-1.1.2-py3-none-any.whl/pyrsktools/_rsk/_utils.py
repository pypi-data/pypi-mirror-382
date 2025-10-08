#!/usr/bin/env python3
# Standard/external imports
from __future__ import annotations
from typing import *
import sys
import numpy.typing as npt
from numpy.lib import recfunctions as rfn


# Module imports
from pyrsktools.datatypes import *

if TYPE_CHECKING:
    from pyrsktools import RSK


def printwarning(message: str) -> None:
    """Static method to print a warning message to stderr.

    Args:
        message (str): message to rpint
    """
    print(message, file=sys.stderr)


def dataexistsorerror(self: RSK, processedData: bool = False) -> None:
    if processedData:
        if self.processedData.size <= 0:
            raise ValueError(
                "RSK instance does not contain any processed data, use RSK.readprocesseddata()."
            )
    else:
        if self.data.size <= 0:
            raise ValueError("RSK instance does not contain any data, use RSK.readdata().")


def getprofilesorerror(
    self: RSK, profiles: Union[int, Collection[int]] = []
) -> List[Tuple[RegionCast, RegionCast, RegionProfile]]:
    """Get profile regions.

    Args:
        profiles (Union[int, Collection[int]], optional): the profile(s) to select. Defaults to [] (all profiles).

    Returns:
        List[Tuple[RegionCast, RegionCast, RegionProfile]]: tuple of (RegionCast,  RegionCast, RegionProfile)

    Get relevant profile regions (e.g., those from RSK.regions), returning a list of tuples. Each tuple
    contains the regions relating to each profile. Tries to get all profiles if profiles is []. If no
    profiles could be found, returns an error.
    """
    profileRegions: List[Tuple[RegionCast, RegionCast, RegionProfile]] = []
    downRegion: RegionCast = None
    upRegion: RegionCast = None
    profileRegion: RegionProfile = None
    profileIndex = 0

    # Turn profiles into a set (potentially empty) for consistency
    profiles = set(profiles) if hasattr(profiles, "__iter__") else {profiles}  # type: ignore
    # We assume RSK.regions is always a sorted immutable tuple.
    # From `Region`, we know sorting will always result in
    # each RegionProfile coming after both of its related RegionCasts
    # (because they have a larger tstamp2). The order will be:
    # (RegionCast, RegionCast, RegionProfile)
    for region in self.regions:
        if isinstance(region, RegionCast):
            if region.isdowncast():
                downRegion = region
            elif region.isupcast():
                upRegion = region
        elif isinstance(region, RegionProfile):
            # if not downRegion or not upRegion: # here requires both upcast and downcast in one profile
            if not downRegion and not upRegion:  # this allows one cast exist under one profile
                raise ValueError("Failed to get profiles due to missing cast region(s)")
            if profileRegion:
                raise ValueError("Failed to get profiles due to extraneous profile region")

            # If not profiles, the user didn't pass any profile indices, so we default to getting all.
            # If they passed in profile indices and our current index is in there, get it.
            if not profiles or profileIndex in profiles:
                profileRegion = region
                # allow single cast appended
                if downRegion and upRegion:
                    # append the cast in the order of time
                    profileRegions.append(
                        (downRegion, upRegion, profileRegion)
                    ) if downRegion.tstamp2 < upRegion.tstamp2 else profileRegions.append(
                        (upRegion, downRegion, profileRegion)
                    )
                else:
                    profileRegions.append(
                        (downRegion, upRegion, profileRegion)
                    )  # either downRegion or upRegion is None

            downRegion, upRegion, profileRegion = None, None, None
            profileIndex += 1

    if not profileRegions:
        raise ValueError("No profile regions found or none that matched the given indices")

    return profileRegions


def channelexists(self: RSK, channel: Union[str, Channel], processedData: bool = False) -> bool:
    # Instead of checking RSK.channels, we check the labelled Numpy
    # columns of RSK.data; the caller cares about this existing
    # more because they will index data as rsk.data["channel_name"]
    channelNames = self.data.dtype.names if not processedData else self.processedData.dtype.names
    if isinstance(channel, Channel):
        return True if channel.longName in channelNames else False
    else:
        return True if channel in channelNames else False


def channelsexistorerror(
    self: RSK,
    channels: Union[Union[str, Channel], Collection[Union[str, Channel]]],
    processedData: bool = False,
) -> None:
    if isinstance(channels, str) or isinstance(channels, Channel):
        channels = [channels]

    for channel in channels:
        if not self.channelexists(channel, processedData):
            channelName = channel.longName if isinstance(channel, Channel) else channel
            raise ValueError(f'Data does not contain required channel: "{channelName}"')


def appendchannel(
    self: RSK, channel: Channel, data: npt.NDArray, isMeasured: int, isDerived: int
) -> None:
    """Given an instance of :class:`Channel` and data to be populated as a column in
    :param:`RSK.data`, this method will take the channel instance, assign it
    an appropriate channelID, append the channel to :param:`RSK.channels`,
    then either overwrite or append the data associated with that channel to :param:`RSK.data`.

    Args:
        channel (Channel): channel instance to append, see :param:`pyrsktools.channels`.
        data (npt.NDArray): the data related to the channel to add.
    """

    if self.channelexists(channel.longName):  # Overwrite values if they exist
        self.data[channel.longName] = data
    else:  # Otherwise, create and append the field
        self.data = rfn.append_fields(
            self.data, channel.longName, data, "float64", fill_value=np.nan, usemask=False
        )
        self.channels.append(
            channel.withnewparams(
                channelID=max(self.channels, key=lambda ch: ch.channelID).channelID + 1,
                isMeasured=isMeasured,
                isDerived=isDerived,
            )
        )


def getchannelnamesandunits(
    self: RSK,
    channels: Union[str, Collection[str]],
    exclude: Optional[Set[str]] = None,
    processedData: bool = False,
) -> Tuple[List[str], List[str]]:
    if exclude and not isinstance(exclude, set):
        raise ValueError("Argument 'exclude' must be of type set")

    if channels and isinstance(channels, str):  # Channels is not an empty list and is a string
        channelNames = [channels]  # Single element list with channel
    elif channels:  # Channels is not empty (and not a string), assume an list and use it
        channelNames = list(channels)  # One or more element list with channel(s)
    else:  # Else, likely an empty list []
        # Use all channels in the data (minus timestamp), unless the respective data field
        # is empty, then default back to RSK.channels field.
        if processedData:
            if self.processedData.size > 0:
                channelNames = list(self.processedData.dtype.names[1:])
            else:
                channelNames = [c.longName for c in self.channels]
        else:
            if self.data.size > 0:
                channelNames = list(self.data.dtype.names[1:])
            else:
                channelNames = [c.longName for c in self.channels]

    # If channel exclusions specified, filter them out
    if exclude:
        channelNames = [name for name in channelNames if name not in exclude]

    # Get channel units relating to names above
    # We could do: [c.units for c in self.channels if c.longName.startswith(channelNames)]
    # but we should iterate over channelNames not self.channels first to ensure we
    # place units in the same order of channelNames (rather than self.channels)
    channelUnits = []
    for name in channelNames:
        channelFound = False
        for c in self.channels:
            if name == c.longName:
                channelUnits.append(c.units)
                channelFound = True
        if not channelFound:
            raise RuntimeError(f"Failed to find channel units for: {name}.")

    return channelNames, channelUnits


def getdbnamesfromlongnames(self: RSK, longNames: Union[str, List[str]]) -> List[str]:
    """Iterates through :obj:`RSK.channels` and tries to find
    channel(s) with matching longName(s). If found, returns
    the database name(s) of the channel(s). If not found, returns
    the given longName(s) back to the caller.

    Args:
        longNames (Union[str, List[str]]): the longName(s) used to determine the channel(s) to
            get the DB name(s) from

    Returns:
        List[str]: a list of channel name(s), where each channel is either the DB name if found,
            or the original longName if not found.
    """
    # Set the default names-to-be-returned as the given longName(s)
    dbNames = [longNames] if isinstance(longNames, str) else list(longNames)

    for i in range(len(dbNames)):
        for channel in self.channels:
            if channel.longName == dbNames[i]:
                dbNames[i] = channel._dbName

    return dbNames
