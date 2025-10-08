#!/usr/bin/env python3
"""
Tests for pyRSKtools RSK view methods.
"""
# Standard/external imports
import unittest
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import rcParams

# Module imports
from pyrsktools import RSK, utils
from pyrsktools.channels import *
from pyrsktools.datatypes import *
from common import GOLDEN_RSK, RSK_FILES_PROFILING
from common import MATLAB_RSK, MATLAB_DATA_DIR
from common import MATLAB_RSK_MOOR


class TestView(unittest.TestCase):
    def test_plotdata(self):
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()

            fig, axes = rsk.plotdata()
            fig, axes = rsk.plotdata(profile=1)
            fig, axes = rsk.plotdata(channels="pressure", showcast=True)
            # fig, axes = rsk.plotdata(channels=["conductivity", "temperature", "dissolved_o2_saturation", "chlorophyll"])
            # plt.show()
        with RSK(MATLAB_RSK_MOOR.as_posix()) as rsk:
            rsk.readdata()
            fig, axes = rsk.plotdata()

    def test_plotprofiles(self):
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()
            rsk.derivesalinity()

            fig, axes = rsk.plotprofiles(
                channels=["conductivity", "temperature", "salinity"],
                profiles=range(0, 8),
                direction="down",
            )
            # fig, axes = rsk.plotprofiles(channels=["chlorophyll", "temperature"])
            # fig, axes = rsk.plotprofiles(channels=["chlorophyll", "temperature"], direction="down")
            # fig, axes = rsk.plotprofiles(profiles=1)
            # plt.show()

        # ----- Generic RSK tests -----
        for f in RSK_FILES_PROFILING:
            print(f)
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
            rsk.deriveseapressure()
            rsk.derivesalinity()

            fig, axes = rsk.plotprofiles(
                channels=["conductivity","temperature"],
                direction="both",
            )
            #plt.show()

    def test_plotprocesseddata(self):

        with RSK(GOLDEN_RSK.as_posix()) as rsk:
            t1, t2 = np.datetime64("2020-10-03T11:30:00"), np.datetime64("2020-10-03T19:20:00")
            rsk.readdata(t1=t1, t2=t2)
            rsk.readprocesseddata(t1=t1, t2=t2)

            fig, axes = rsk.mergeplots(
                rsk.plotprocesseddata(channels="pressure"),
                rsk.plotdata(channels="pressure"),
            )
            #plt.show()

            # fig, axes = rsk.plotprocesseddata()
            # fig, axes = rsk.plotprocesseddata(channels="pressure")
            # with plt.style.context({"lines.markersize": 10, "lines.linestyle": "-."}):
            #     plt.show()

    def test_images(self):
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()
            rsk.binaverage(binSize=0.5, direction="down")

            fig, axes = rsk.images(channels="temperature", direction="down")
            fig, axes = rsk.images(channels="temperature", direction="down", showgap=True)
            fig, axes = rsk.images([Chlorophyll.longName])
            fig, axes = rsk.images(Chlorophyll.longName, showgap=True)
            fig, axes = rsk.images(Chlorophyll.longName, showgap=True, threshold=400)
            # plt.show()

    def test_plotTS(self):
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.derivesalinity()

            # fig, axes = rsk.plotTS(direction="down")
            # fig, axes = rsk.plotTS(isopycnal=10)
            fig, axes = rsk.plotTS(profiles=range(3), direction="down", isopycnal=10)
            # plt.show()


if __name__ == "__main__":
    unittest.main()
