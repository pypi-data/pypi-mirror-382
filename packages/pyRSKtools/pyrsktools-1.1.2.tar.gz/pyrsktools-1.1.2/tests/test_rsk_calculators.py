#!/usr/bin/env python3
"""
Tests for pyRSKtools RSK calculators methods.
"""
# Standard/external imports
import unittest
import json
import numpy as np

# Module imports
from pyrsktools import RSK, utils
from pyrsktools.channels import *
from pyrsktools.datatypes import *
from common import RSK_FILES, MATLAB_RSK, MATLAB_DATA_DIR, BPR_RSK, APT_CERVELLO_RSK, RSK_FILES_BPR
from common import CSV_FILES, GOLDEN_CSV
from common import readMatlabFile, readMatlabChannelDataByName


class TestCalculators(unittest.TestCase):
    def test_derivesalinity(self):
        channel = Salinity
        channelName = channel.longName

        # ----- Matlab RSK tests -----
        mValues = readMatlabChannelDataByName(
            readMatlabFile("RSKderivesalinity.json"), channel._dbName
        )

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.derivesalinity()
            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-06))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()

                # If no conductivity, we can't proceed, so expect an error then move on
                if not rsk.channelexists(Conductivity):
                    with self.assertRaises(ValueError):
                        rsk.derivesalinity()
                    continue

                hasGiven = False
                if rsk.channelexists(channelName):
                    given = rsk.data[channelName].copy()
                    given_sp = rsk.data["sea_pressure"].copy()
                    given_t = rsk.data["temperature"].copy()
                    hasGiven = True

                    # Filter out the values out of PSS-78 range in the test: https://salinometry.com/pss-78/
                    # In GSW, if the PSS-78 algorithm produces a Practical Salinity that is less than 2
                    # then the Practical Salinity is recalculated with a modified form of the Hill et al. (1986) formula.
                    # The modification of the Hill et al. (1986) expression is to ensure that it is exactly consistent with PSS-78 at SP = 2.
                    #  Practical salinity: 2 to 42
                    given[(given < 2) | (given > 42)] = np.nan
                    rsk.data[channelName][
                        (rsk.data[channelName] < 2) | (rsk.data[channelName] > 42)
                    ] = np.nan
                    #  Sea pressure: 0 to 10000 dbar
                    given[(given_sp < 0) | (given_sp > 10000)] = np.nan
                    rsk.data[channelName][
                        (rsk.data["sea_pressure"] < 0) | (rsk.data["sea_pressure"] > 10000)
                    ] = np.nan
                    #  Temperature: -2 to 35 degree C
                    given[(given_t < -2) | (given_t > 35)] = np.nan
                    rsk.data[channelName][
                        (rsk.data["temperature"] < -2) | (rsk.data["temperature"] > 35)
                    ] = np.nan

                rsk.derivesalinity()  # Overwrites salinity
                self.assertTrue(rsk.channelexists(channelName))
                self.assertTrue(any(ch.longName == channelName for ch in rsk.channels))

                if hasGiven:
                    # Filter out nan values, they screw up our comparison
                    mask = ~(
                        np.isnan(given)
                        | np.isnan(rsk.data[channelName])
                        | np.ma.getmask(rsk.data[channelName])
                    )
                    # If had given, check we are "close" to the given
                    self.assertTrue(
                        np.allclose(given[mask], rsk.data[channelName][mask], atol=1e-03)
                    )

                # Make sure we deny invalid seawater library parameters
                with self.assertRaises(ValueError):
                    rsk.derivesalinity(seawaterLibrary="Invalid")

    def test_deriveseapressure(self):
        channel = SeaPressure
        channelName = channel.longName

        # ----- Golden RSK tests -----
        mValues = readMatlabChannelDataByName(
            readMatlabFile("RSKderiveseapressure.json"), channel._dbName
        )

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()
            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-10))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            print(f)
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()

                default_patm = 10.1325
                custom_patm = 9
                variable_patm = np.linspace(10, 10.4, len(rsk.data))
                for param in rsk.parameterKeys:
                    # If parameterKey exists, use that as the default value
                    if param.key == "ATMOSPHERE":
                        default_patm = float(param.value)

                hasGiven = False
                if rsk.channelexists(channelName):
                    given = rsk.data[channelName].copy()
                    hasGiven = True

                rsk.deriveseapressure()  # Overwrites sea pressure

                if hasGiven:
                    # Filter out nan values, they screw up our comparison
                    mask = ~(
                        np.isnan(given)
                        | np.isnan(rsk.data[channelName])
                        | np.ma.getmask(rsk.data[channelName])
                    )
                    # If had given, check we are "close" to the given
                    self.assertTrue(
                        np.allclose(given[mask], rsk.data[channelName][mask], atol=1e-06)
                    )

                # If the data has a Pressure channel, i.e., it didn't default to 0, we can do some additional tests
                if rsk.channelexists(Pressure):
                    # Test with: default patm value
                    self.assertTrue(
                        np.allclose(
                            rsk.data[channelName],
                            rsk.data[Pressure.longName] - default_patm,
                            equal_nan=True,
                        )
                    )
                    self.assertTrue(any(ch.longName == channelName for ch in rsk.channels))

                    # Custom patm value
                    rsk.deriveseapressure(patm=custom_patm)
                    self.assertTrue(
                        np.allclose(
                            rsk.data[channelName],
                            rsk.data[Pressure.longName] - custom_patm,
                            equal_nan=True,
                        )
                    )
                    # Variable patm
                    rsk.deriveseapressure(patm=variable_patm)
                    self.assertTrue(
                        np.allclose(
                            rsk.data[channelName],
                            rsk.data[Pressure.longName] - variable_patm,
                            equal_nan=True,
                        )
                    )

    def test_derivedepth(self):
        channel = Depth
        channelName = channel.longName

        # ----- Golden RSK tests -----
        mValues = readMatlabChannelDataByName(
            readMatlabFile("RSKderivedepth.json"), channel._dbName
        )

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()
            rsk.derivedepth()
            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-02))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                rsk.deriveseapressure()

                hasGiven = False
                if rsk.channelexists(channelName):
                    given = rsk.data[channelName].copy()
                    hasGiven = True

                rsk.derivedepth()  # Overwrites depth
                self.assertTrue(rsk.channelexists(channelName))
                self.assertTrue(any(ch.longName == channelName for ch in rsk.channels))

                if hasGiven:
                    # Filter out nan values, they screw up our comparison
                    mask = ~(
                        np.isnan(given)
                        | np.isnan(rsk.data[channelName])
                        | np.ma.getmask(rsk.data[channelName])
                    )
                    # If had given, check we are "close" to the given
                    self.assertTrue(
                        np.allclose(given[mask], rsk.data[channelName][mask], atol=1e-00)
                    )

                # Make sure we deny invalid seawater library parameters
                with self.assertRaises(ValueError):
                    rsk.derivesalinity(seawaterLibrary="Invalid")

    def test_derivevelocity(self):
        channel = Velocity
        channelName = channel.longName

        # ----- Golden RSK tests -----
        mValues = readMatlabChannelDataByName(
            readMatlabFile("RSKderivevelocity.json"), channel._dbName
        )

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()
            rsk.derivedepth()
            rsk.derivevelocity()

            mask = ~(np.isnan(mValues) | np.isnan(rsk.data[channelName]))
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)

            # print("m vs py: ", mValues[0:5], rsk.data[channelName][0:5])
            self.assertTrue(
                np.allclose(
                    mValues[mask],
                    rsk.data[channelName][mask],
                    atol=1e-03,
                    equal_nan=True,
                )
            )

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                rsk.deriveseapressure()

                # If the current RSK doesn't have depth, derive it
                if not rsk.channelexists(Depth):
                    # Since we don't have depth yet, we expect derivevelocity to raise an error
                    with self.assertRaises(ValueError):
                        rsk.derivevelocity()
                    # Now derive depth so we can continue with subsequent testing
                    rsk.derivedepth()

                hasGiven = False
                if rsk.channelexists(channelName):
                    given = rsk.data[channelName].copy()
                    hasGiven = True

                rsk.derivevelocity()  # Overwrites velocity
                self.assertTrue(rsk.channelexists(channelName))
                self.assertTrue(any(ch.longName == channelName for ch in rsk.channels))

                if hasGiven:
                    # Filter out nan values, they screw up our comparison
                    mask = ~(
                        np.isnan(given)
                        | np.isnan(rsk.data[channelName])
                        | np.ma.getmask(rsk.data[channelName])
                    )
                    # If had given, check we are "close" to the given
                    self.assertTrue(
                        np.allclose(given[mask], rsk.data[channelName][mask], atol=1e-03)
                    )

    def test_deriveC25(self):
        channel = SpecificConductivity
        channelName = channel.longName

        # ----- Golden RSK tests -----
        mValues = readMatlabChannelDataByName(readMatlabFile("RSKderiveC25.json"), channel._dbName)

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveC25()
            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-02))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()

                # If the current RSK doesn't have conductivity or temperature, expect ValueError
                if not rsk.channelexists(Conductivity) or not rsk.channelexists(Temperature):
                    with self.assertRaises(ValueError):
                        rsk.deriveC25()
                    continue

                hasGiven = False
                if rsk.channelexists(channelName):
                    given = rsk.data[channelName].copy()
                    hasGiven = True

                rsk.deriveC25()  # Overwrites specific conductivity
                self.assertTrue(rsk.channelexists(channelName))
                self.assertTrue(any(ch.longName == channelName for ch in rsk.channels))

                if hasGiven:
                    # Filter out nan values, they screw up our comparison
                    mask = ~(
                        np.isnan(given)
                        | np.isnan(rsk.data[channelName])
                        | np.ma.getmask(rsk.data[channelName])
                    )
                    # If had given, check we are "close" to the given
                    self.assertTrue(
                        np.allclose(given[mask], rsk.data[channelName][mask], atol=1e-03)
                    )

    def test_deriveBPR(self):
        with RSK(BPR_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveBPR()

            pyChannels = rsk.channelNames
            mChannels = [
                "Temperature",
                "Barometer pressure period",
                "Barometer temperature period",
                "Period1",
                "Period2",
                "Period3",
                "Period4",
                "BPR pressure1",
                "BPR temperature1",
                "BPR pressure2",
                "BPR temperature2",
                "Barometer pressure",
                "Barometer temperature",
            ]

            mFile = MATLAB_DATA_DIR / "RSKderiveBPR.json"
            with mFile.open("r") as fd:
                mRSK = json.load(fd)
            for i in range(len(mChannels)):
                mData = readMatlabChannelDataByName(mRSK, mChannels[i])
                # self.assertTrue(np.allclose(mData,rsk.data[pyChannels[i]], atol = 1e-07, equal_nan =True))
                self.assertTrue(np.equal(mData, rsk.data[pyChannels[i]]).all())
                print("pass: ", pyChannels[i])

        # test different versions of quartzQ with different channel shortNames
        for f in RSK_FILES_BPR:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                rsk.deriveBPR()
                self.assertIn("bpr_pressure", rsk.channelNames)
                self.assertIn("bpr_temperature", rsk.channelNames)

    def test_deriveO2(self):
        validDerives = {"concentration", "saturation"}
        validUnits = {"µmol/l", "ml/l", "mg/l"}

        # ----- Matlab RSK tests -----
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.derivesalinity()

            rsk.deriveO2(toDerive="concentration")  # Get concentration from current saturation
            channelName = DissolvedO2Concentration.longName
            mValues = readMatlabChannelDataByName(
                readMatlabFile("RSKderiveO2.json"), "Dissolved O22"
            )
            mask = ~(np.isnan(mValues) | np.isnan(rsk.data[channelName]))
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-02))

            rsk.deriveO2(toDerive="saturation")  # Overwrite/recalculate current saturation
            channelName = DissolvedO2Saturation.longName
            mValues = readMatlabChannelDataByName(
                readMatlabFile("RSKderiveO2.json"), "Dissolved O2"
            )
            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-01))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()

                with self.assertRaises(ValueError):
                    rsk.deriveO2(toDerive="invalid")

                with self.assertRaises(ValueError):
                    rsk.deriveO2(unit="invalid")

                # If no conductivity, we can't proceed, so expect an error then move on
                if not rsk.channelexists(Conductivity):
                    with self.assertRaises(ValueError):
                        rsk.deriveO2()
                    continue

                if not rsk.channelexists(Temperature) or not rsk.channelexists(Salinity):
                    # If the current RSK doesn't have temperature or salinity, expect ValueError
                    with self.assertRaises(ValueError):
                        rsk.deriveO2()

                    # If we have temperature but not salinity, derive salinity so we can do further tests,
                    # otherwise skip this RSK
                    if rsk.channelexists(Temperature):
                        rsk.derivesalinity()
                    else:
                        continue

                # ------ Test deriving concentration ------
                channelName = DissolvedO2Concentration.longName
                hasGiven = False
                if rsk.channelexists(channelName):
                    # print(f)
                    given = rsk.data[channelName].copy()
                    hasGiven = True

                # If O2 saturation exists, we can try to calculate concentration
                if rsk.channelexists(DissolvedO2Saturation):
                    rsk.deriveO2(toDerive="concentration")
                    if hasGiven:
                        # Filter out nan values, they screw up our comparison
                        mask = ~(
                            np.isnan(given)
                            | np.isnan(rsk.data[channelName])
                            | np.ma.getmask(rsk.data[channelName])
                        )
                        # If had given, check we are "close" to the given
                        self.assertTrue(
                            np.allclose(given[mask], rsk.data[channelName][mask], atol=1e-03)
                        )
                else:
                    # We also expect an error to occur if we try to derive concentration without saturation
                    with self.assertRaises(ValueError):
                        rsk.deriveO2(toDerive="concentration")

                # ------ Test deriving saturation ------
                channelName = DissolvedO2Saturation.longName
                hasGiven = False
                if rsk.channelexists(channelName):
                    given = rsk.data[channelName].copy()
                    hasGiven = True

                # If O2 concentration exists (potentially calculated above), we can try to calculate saturation
                if rsk.channelexists(DissolvedO2Concentration):
                    rsk.deriveO2(toDerive="saturation")
                    if hasGiven:
                        # Filter out nan values, they screw up our comparison
                        mask = ~(
                            np.isnan(given)
                            | np.isnan(rsk.data[channelName])
                            | np.ma.getmask(rsk.data[channelName])
                        )

                        # If had given, check we are "close" to the given
                        self.assertTrue(
                            np.allclose(given[mask], rsk.data[channelName][mask], atol=0.1)
                        )
                else:
                    # We also expect an error to occur if we try to derive saturation without concentration
                    with self.assertRaises(ValueError):
                        rsk.deriveO2(toDerive="saturation")

    def test_derivebuoyancy(self):
        # ----- Golden RSK tests -----

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            mRSK = readMatlabFile("RSKderivebuoyancy.json")
            rsk.readdata()
            rsk.derivesalinity()
            rsk.deriveseapressure()
            rsk.derivebuoyancy()

            channelName = BuoyancyFrequencySquared.longName
            mValues = readMatlabChannelDataByName(mRSK, BuoyancyFrequencySquared._dbName)
            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-06))

            channelName = Stability.longName
            mValues = readMatlabChannelDataByName(mRSK, Stability._dbName)
            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-06))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()

                # If no salinity, try to derive it
                if not rsk.channelexists(Salinity):
                    try:
                        rsk.derivesalinity()
                    except Exception:
                        pass

                # If no sea pressure, try to derive it
                if not rsk.channelexists(SeaPressure):
                    try:
                        rsk.deriveseapressure()
                    except Exception:
                        pass

                # If the current RSK doesn't have needed channels, expect ValueError
                if (
                    not rsk.channelexists(Temperature)
                    or not rsk.channelexists(Salinity)
                    or not rsk.channelexists(SeaPressure)
                ):
                    with self.assertRaises(ValueError):
                        rsk.derivebuoyancy()
                    continue

                # Buoyancy (B) and stability (S)
                hasBGiven, hasSGiven = False, False
                if rsk.channelexists(BuoyancyFrequencySquared):
                    bGiven = rsk.data[BuoyancyFrequencySquared.name].copy()
                    hasBGiven = True
                if rsk.channelexists(Stability):
                    sGiven = rsk.data[Stability.name].copy()
                    hasSGiven = True

                rsk.derivebuoyancy()
                self.assertTrue(rsk.channelexists(BuoyancyFrequencySquared))
                self.assertTrue(
                    any(ch.longName == BuoyancyFrequencySquared.longName for ch in rsk.channels)
                )
                self.assertTrue(rsk.channelexists(Stability))
                self.assertTrue(any(ch.longName == Stability.longName for ch in rsk.channels))

                if hasBGiven:
                    # Filter out nan values, they screw up our comparison
                    mask = ~(
                        np.isnan(bGiven) | np.isnan(rsk.data[BuoyancyFrequencySquared.longName])
                    )
                    # If had given, check we are "close" to the given
                    self.assertTrue(
                        np.allclose(
                            bGiven[mask],
                            rsk.data[BuoyancyFrequencySquared.longName][mask],
                            atol=1e-03,
                        )
                    )

                if hasSGiven:
                    # Filter out nan values, they screw up our comparison
                    mask = ~(np.isnan(sGiven) | np.isnan(rsk.data[Stability.longName]))
                    # If had given, check we are "close" to the given
                    self.assertTrue(
                        np.allclose(
                            sGiven[mask],
                            rsk.data[Stability.longName][mask],
                            atol=1e-03,
                        )
                    )

    def test_derivesigma(self):
        channel = DensityAnomaly
        channelName = channel.longName

        # ----- Golden RSK tests -----
        mValues = readMatlabChannelDataByName(
            readMatlabFile("RSKderivesigma.json"), channel._dbName
        )

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.derivesalinity()
            rsk.deriveseapressure()
            rsk.derivesigma()

            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-03))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()

                # If the current RSK doesn't have conductivity or temperature, expect ValueError
                if (
                    not rsk.channelexists(Temperature)
                    or not rsk.channelexists(Salinity)
                    or not rsk.channelexists(SeaPressure)
                ):
                    with self.assertRaises(ValueError):
                        rsk.derivesigma()

                    # If we have everything but sea pressure, derive it so we can test further,
                    # else continue
                    if rsk.channelexists(Temperature) and rsk.channelexists(Salinity):
                        rsk.deriveseapressure()
                    else:
                        continue

                hasGiven = False
                if rsk.channelexists(channelName):
                    given = rsk.data[channelName].copy()
                    hasGiven = True

                with self.assertRaises(ValueError):
                    rsk.derivesigma([1] * len(rsk.data))

                with self.assertRaises(ValueError):
                    rsk.derivesigma([1] * len(rsk.data), [1] * (len(rsk.data) - 1))

                rsk.derivesigma()  # Overwrites specific conductivity
                self.assertTrue(rsk.channelexists(channelName))
                self.assertTrue(any(ch.longName == channelName for ch in rsk.channels))

                if hasGiven:
                    # Filter out nan values, they screw up our comparison
                    mask = ~(
                        np.isnan(given)
                        | np.isnan(rsk.data[channelName])
                        | np.ma.getmask(rsk.data[channelName])
                    )
                    # If had given, check we are "close" to the given
                    self.assertTrue(
                        np.allclose(given[mask], rsk.data[channelName][mask], atol=1e-03)
                    )

    def test_deriveSA(self):
        channel = AbsoluteSalinity
        channelName = channel.longName

        # ----- Golden RSK tests -----
        mValues = readMatlabChannelDataByName(readMatlabFile("RSKderiveSA.json"), channel._dbName)

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.derivesalinity()
            rsk.deriveseapressure()
            rsk.deriveSA()

            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-06))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()

                if not rsk.channelexists(Salinity) or not rsk.channelexists(SeaPressure):
                    with self.assertRaises(ValueError):
                        rsk.deriveSA()

                    # If we have everything but sea pressure, derive it so we can test further,
                    # else continue
                    if rsk.channelexists(Salinity):
                        rsk.deriveseapressure()
                    else:
                        continue

                hasGiven = False
                if rsk.channelexists(channelName):
                    given = rsk.data[channelName].copy()
                    hasGiven = True

                with self.assertRaises(ValueError):
                    rsk.deriveSA([1] * len(rsk.data))

                with self.assertRaises(ValueError):
                    rsk.deriveSA([1] * len(rsk.data), [1] * (len(rsk.data) - 1))

                rsk.deriveSA()
                self.assertTrue(rsk.channelexists(channelName))
                self.assertTrue(any(ch.longName == channelName for ch in rsk.channels))

                if hasGiven:
                    # Filter out nan values, they screw up our comparison
                    mask = ~(
                        np.isnan(given)
                        | np.isnan(rsk.data[channelName])
                        | np.ma.getmask(rsk.data[channelName])
                    )
                    # If had given, check we are "close" to the given
                    self.assertTrue(
                        np.allclose(given[mask], rsk.data[channelName][mask], atol=1e-03)
                    )

    def test_derivetheta(self):
        channel = PotentialTemperature
        channelName = channel.longName

        # ----- Golden RSK tests -----
        mValues = readMatlabChannelDataByName(
            readMatlabFile("RSKderivetheta.json"), channel._dbName
        )

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.derivesalinity()
            rsk.deriveseapressure()
            rsk.derivetheta()

            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-06))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()

                if (
                    not rsk.channelexists(Temperature)
                    or not rsk.channelexists(Salinity)
                    or not rsk.channelexists(SeaPressure)
                ):
                    with self.assertRaises(ValueError):
                        rsk.derivetheta()

                    if rsk.channelexists(Temperature) and rsk.channelexists(Salinity):
                        rsk.deriveseapressure()
                    else:
                        continue

                hasGiven = False
                if rsk.channelexists(channelName):
                    given = rsk.data[channelName].copy()
                    hasGiven = True

                with self.assertRaises(ValueError):
                    rsk.derivetheta([1] * len(rsk.data))

                with self.assertRaises(ValueError):
                    rsk.derivetheta([1] * len(rsk.data), [1] * (len(rsk.data) - 1))

                rsk.derivetheta()
                self.assertTrue(rsk.channelexists(channelName))
                self.assertTrue(any(ch.longName == channelName for ch in rsk.channels))

                if hasGiven:
                    # Filter out nan values, they screw up our comparison
                    mask = ~(
                        np.isnan(given)
                        | np.isnan(rsk.data[channelName])
                        | np.ma.getmask(rsk.data[channelName])
                    )
                    # If had given, check we are "close" to the given
                    self.assertTrue(
                        np.allclose(given[mask], rsk.data[channelName][mask], atol=1e-03)
                    )

    def test_derivesoundspeed(self):
        channel = SpeedOfSound
        channelName = channel.longName

        # ----- Golden RSK tests -----
        mValues = readMatlabChannelDataByName(
            readMatlabFile("RSKderivesoundspeed.json"), channel._dbName
        )

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.derivesalinity()
            rsk.deriveseapressure()
            rsk.derivesoundspeed()

            mask = ~(
                np.isnan(mValues)
                | np.isnan(rsk.data[channelName])
                | np.ma.getmask(rsk.data[channelName])
            )
            self.assertGreater(len(rsk.data[channelName][mask]), 10000)
            self.assertTrue(np.allclose(mValues[mask], rsk.data[channelName][mask], atol=1e-06))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()

                with self.assertRaises(ValueError):
                    rsk.derivesoundspeed(soundSpeedAlgorithm="invalid")

                if (
                    not rsk.channelexists(Temperature)
                    or not rsk.channelexists(Salinity)
                    or not rsk.channelexists(SeaPressure)
                ):
                    with self.assertRaises(ValueError):
                        rsk.derivesoundspeed()

                    if rsk.channelexists(Temperature) and rsk.channelexists(Salinity):
                        rsk.deriveseapressure()
                    else:
                        continue

                for alg in ["UNESCO", "DelGrosso", "Wilson"]:
                    rsk.derivesoundspeed(soundSpeedAlgorithm=alg)
                    self.assertTrue(rsk.channelexists(channelName))
                    self.assertTrue(any(ch.longName == channelName for ch in rsk.channels))

    def test_deriveA0A(self):
        with RSK(BPR_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveBPR()
            rsk.deriveA0A()

            pyChannels = rsk.channelNames
            mChannels = [
                "Temperature",
                "Barometer pressure period",
                "Barometer temperature period",
                "Period1",
                "Period2",
                "Period3",
                "Period4",
                "BPR pressure1",
                "BPR temperature1",
                "BPR pressure2",
                "BPR temperature2",
                "Barometer pressure",
                "Barometer temperature",
                "BPR corrected pressure1",
                "Pressure drift1",
                "BPR corrected pressure2",
                "Pressure drift2",
            ]

            mFile = MATLAB_DATA_DIR / "RSKderiveA0A.json"
            with mFile.open("r") as fd:
                mRSK = json.load(fd)
            for i in range(len(mChannels)):
                mData = readMatlabChannelDataByName(mRSK, mChannels[i])
                self.assertTrue(
                    np.allclose(mData, rsk.data[pyChannels[i]], atol=1e-04, equal_nan=True)
                )

    def test_deriveAPT(self):
        Acceleration_coefficients = [
            [166.34824076, 156.24548496, -163.35657396],
            [-5.328037, -17.1992, 12.40078],
            [-261.0626, -342.8823, 215.658],
            [0.03088299, 0.03029925, 0.03331123],
            [0, 0, 0],
            [29.04551984, 29.65519865, 29.19887879],
            [-0.291685, 1.094704, 0.276486],
            [24.50986, 31.78739, 30.48166],
            [0, 0, 0],
            [0, 0, 0],
        ]
        Alignment_coefficients = [
            [1.00024800955343, -0.00361697821901, -0.01234855907175],
            [-0.00361697821901, 1.0000227853442, -0.00151293870726],
            [-0.01234855907175, 0.00151293870726, 1.00023181988111],
        ]
        Temperature_coefficients = [
            [5.795742, 5.795742, 5.795742],
            [-3938.81, -3938.684, -3938.464],
            [-9953.514, -9947.209, -9962.304],
            [0, 0, 0],
        ]
        with RSK(APT_CERVELLO_RSK.as_posix()) as rsk:
            rsk.readdata()
            # rsk.deriveBPR()
            rsk.deriveAPT(
                Alignment_coefficients, Temperature_coefficients, Acceleration_coefficients
            )
            pyChannels = rsk.channelNames[-4:]
            mChannels = [
                "X acceleration",
                "Y acceleration",
                "Z acceleration",
                "APT temperature",
            ]

            mFile = MATLAB_DATA_DIR / "RSKderiveAPT.json"
            with mFile.open("r") as fd:
                mRSK = json.load(fd)
            for i in range(len(mChannels)):
                mData = readMatlabChannelDataByName(mRSK, mChannels[i])
                self.assertTrue(
                    np.allclose(mData, rsk.data[pyChannels[i]], atol=1e-08, equal_nan=True)
                )
            # acceleration near 1G
            pyG = np.sqrt(
                rsk.data["x_axis_acceleration"] ** 2
                + rsk.data["y_axis_acceleration"] ** 2
                + rsk.data["z_axis_acceleration"] ** 2
            )
            self.assertTrue(
                np.allclose(pyG, 9.8 * np.ones(np.shape(pyG)), atol=1e-01, equal_nan=True)
            )


if __name__ == "__main__":
    unittest.main()
