#!/usr/bin/env python3
"""
Tests for pyRSKtools RSK export methods.
"""
# Standard/external imports
import unittest
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import inspect
from random import randint

# Module imports
from pyrsktools import RSK, utils
from pyrsktools.channels import *
from pyrsktools.datatypes import *
from common import GOLDEN_RSK
from common import MATLAB_RSK, MATLAB_DATA_DIR


class TestExport(unittest.TestCase):
    OUTPUT_DIR = "/tmp"

    def test_RSK2CSV(self):
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()

            # Test 1: test that all arguments works
            # TODO: add additional tests here, this just just that it actually runs unless
            # the tester manually examines the output
            rsk.RSK2CSV(
                outputDir=self.OUTPUT_DIR, channels=["temperature", "pressure"], profiles=[0, 2]
            )

            # Test 2: test data is same length when exporting the entire struct to CSV
            rsk.RSK2CSV(outputDir=self.OUTPUT_DIR)
            expectedOutputFile = f"{self.OUTPUT_DIR}/{MATLAB_RSK.stem}.csv"
            self.assertTrue(os.path.isfile(expectedOutputFile))

            with open(expectedOutputFile, "r") as fd:
                reader = csv.reader(fd)
                csvDataSize = sum(
                    1 for row in reader if len(row) > 0 and not row[0].startswith("//")
                )
                self.assertEqual(rsk.data.size, csvDataSize)

    def test_RSK2RSK(self):
        outputDir = "/tmp"

        attrs = {
            "instrumentSensors",
            "ranging",
            "deployment",
            "channels",
            "calibrations",
            "schedule",
            "scheduleInfo",
            "parameters",
            "dbInfo",
            "version",
            "appSettings",
            "instrument",
            "epoch",
            "instrumentChannels",
            "parameterKeys",
            "power",
            "processedData",
            "data",
        }

        with RSK(MATLAB_RSK.as_posix(), readHiddenChannels=True) as rsk:
            rsk.readdata()
            rsk.readprocesseddata()
            suffix = randint(0, 1000000)
            generatedRskName = rsk.RSK2RSK(outputDir=outputDir, suffix=f"{suffix}")

            with RSK(f"{outputDir}/{generatedRskName}", readHiddenChannels=True) as rskReloaded:
                rskReloaded.readdata()
                rskReloaded.readprocesseddata()

                for attr in attrs:
                    if isinstance(getattr(rsk, attr), np.ndarray):
                        rskArray = getattr(rsk, attr)
                        rskReloadedArray = getattr(rskReloaded, attr)
                        if attr == "data":
                            allequal = np.all(
                                [
                                    np.allclose(
                                        rskArray[name], rskReloadedArray[name], equal_nan=True
                                    )
                                    for name in rsk.channelNames
                                ]
                            )
                        elif attr == "processedData":
                            allequal = np.all(
                                [
                                    np.allclose(
                                        rskArray[name], rskReloadedArray[name], equal_nan=True
                                    )
                                    for name in rsk.processedChannelNames
                                ]
                            )
                        else:
                            raise ValueError(f"Unknown array attribute: {attr}")

                        self.assertTrue(allequal)
                    else:
                        self.assertEqual(getattr(rsk, attr), getattr(rskReloaded, attr))


if __name__ == "__main__":
    unittest.main()
