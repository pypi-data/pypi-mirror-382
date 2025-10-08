#!/usr/bin/env python3
"""
Tests for pyRSKtools RSK other methods.
"""
# Standard/external imports
import unittest
import numpy as np
from contextlib import redirect_stdout
import io
import gsw

# Module imports
from pyrsktools import RSK, utils
from pyrsktools.channels import *
from pyrsktools.datatypes import *
from common import GOLDEN_RSK, RSK_FILES
from common import MATLAB_RSK


class TestOther(unittest.TestCase):
    def test_create(self):
        timestamps = [
            np.datetime64(1651550400000, "ms"),
            np.datetime64(1651550402000, "ms"),
            np.datetime64(1651550404000, "ms"),
        ]
        values = [
            np.array([39.9973, 16.2695, 10.1034], "double"),
            np.array([39.9873, 16.2648, 10.1266], "double"),
            np.array([39.9887, 16.2553, 10.1247], "double"),
        ]
        channels = ["conductivity", "temperature", "pressure"]
        units = ["mS/cm", "°C", "dbar"]
        rsk = RSK.create(timestamps=timestamps, values=values, channels=channels, units=units)

        self.assertEqual(rsk.data.dtype.names[0], "timestamp")
        for i, c in enumerate(rsk.channels):
            self.assertEqual(rsk.channels[i].units, units[i])
            self.assertEqual(rsk.channels[i].longName, channels[i])
            self.assertEqual(rsk.data.dtype.names[i + 1], channels[i])

        for i in range(len(timestamps)):
            self.assertEqual(rsk.data["timestamp"][i], timestamps[i])
            self.assertTrue(np.all(np.equal(rsk.data[i].tolist()[1:], values[i])))

    def test_addchannel(self):
        with RSK(GOLDEN_RSK.as_posix()) as rsk:
            rsk.readdata()

            data = gsw.SA_from_SP(rsk.data["salinity"], rsk.data["sea_pressure"], -150, 49)
            rsk.addchannel(data, "absolute_salinity", units="g/kg", isMeasured=0, isDerived=1)
            self.assertTrue(
                any(
                    True
                    for c in rsk.channels
                    if c.longName == "absolute_salinity" and c.units == "g/kg"
                )
            )
            self.assertTrue(np.all(np.equal(rsk.data["absolute_salinity"], data)))

            data = np.ones(rsk.data.size)
            rsk.addchannel(data, "scooby d0o", units="ruhro", isMeasured=0, isDerived=1)
            self.assertTrue(
                any(
                    True
                    for c in rsk.channels
                    if c.longName == "scooby d0o"
                    and c.units == "ruhro"
                    and c.isDerived == 1
                    and c.isMeasured == 0
                )
            )
            self.assertTrue(np.all(np.equal(rsk.data["scooby d0o"], data)))

    def test_removecasts(self):
        for direction in ("up", "down"):
            with RSK(GOLDEN_RSK.as_posix()) as rsk:
                rsk.readdata()
                originalLen = rsk.data.size
                numberInDirection = np.concatenate(rsk.getprofilesindices(direction=direction)).size

                rsk.removecasts(direction)

                self.assertEqual(originalLen - numberInDirection, rsk.data.size)
                for r in rsk.regions:
                    if isinstance(r, RegionCast) and r.regionType.lower() == direction:
                        raise ValueError(f"There should be no {direction}casts at this point")

    def test_printchannels(self):
        with redirect_stdout(io.StringIO()):
            for f in RSK_FILES:
                with RSK(f.as_posix()) as rsk:
                    # Also sneak in printing the actual RSK class,
                    # i.e, the RSK.__str__().
                    print(rsk)
                    # Then test printing actual channels
                    rsk.printchannels()


if __name__ == "__main__":
    unittest.main()
