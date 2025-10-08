#!/usr/bin/env python3
"""
Tests for pyRSKtools RSK post-processor methods.
"""
# Standard/external imports
from ast import With
import profile
from re import I
from statistics import median
import unittest
import numpy as np

# Module imports
from pyrsktools import RSK, utils
from pyrsktools import channels
from pyrsktools._rsk.read import getprofilesindices
from pyrsktools.channels import *
from pyrsktools.datatypes import *
from common import RSK_FILES, RSK_FILES_PROFILING
from common import MATLAB_RSK, GOLDEN_RSK, MATLAB_RSK_MOOR, BPR_RSK
from common import (
    readMatlabFile,
    readMatlabChannelDataByName,
    Timer,
    getProfileData,
    readMatlabIndices,
    readMatlabProfileDataWithNaN,
)
from datetime import datetime, timedelta


class TestPostProcessors(unittest.TestCase):
    def test_calculateCTlag(self):
        # ----- Matlab RSK tests -----

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()

            # Test 1, values come from Matlab: RSKreadprofiles(RSK, 'profile', 1:15, 'direction', 'down');
            expected = [1] * 15
            lags = rsk.calculateCTlag(profiles=range(15), direction="down")
            self.assertEqual(lags, expected)

            # Test 2, values come from Matlab: RSKreadprofiles(RSK, 'profile', 1:15);
            expected = [
                int(i)
                for i in "1,0,1,0,1,0,1,0,1,20,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0".split(",")
            ]
            lags = rsk.calculateCTlag(profiles=range(15))
            self.assertEqual(lags, expected)

        # ----- Generic RSK tests -----
        for f in RSK_FILES_PROFILING:
            # print(f)
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                rsk.deriveseapressure()
                lags = rsk.calculateCTlag(direction="both")
                # print(lags)

    def test_alignchannel(self):
        # ----- Matlab RSK tests -----

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            # ---- Test 1: shift temperature channel of first four profiles with the same lag value. ----
            # ---- RSKalignchannel(RSK_prof, 'channel', 'Temperature1', 'lag', 2)
            rsk.readdata()
            mRSK = readMatlabFile("RSKalignchannel_test1.json")

            rsk.alignchannel(channel=Temperature.longName, lag=2)
            for pyProfileData, mProfileData in getProfileData(rsk, mRSK):
                self.assertTrue(np.equal(pyProfileData, mProfileData).all())
                # self.assertTrue(np.allclose(pyProfileData, mProfileData, atol=1e-3, equal_nan=True))

            # ---- Test 2: shift oxygen channel of first 4 profiles with profile-specific lags. ----
            # ---- RSKalignchannel(RSK_prof, 'channel', 'Dissolved O2', 'lag', [2 1 -1 0], 'direction','down','profile',1:4)
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            mRSK = readMatlabFile("RSKalignchannel_test2.json")

            rsk.alignchannel(
                channel=DissolvedO2Saturation.longName,
                lag=[2, 1, -1, 0],
                direction="down",
                profiles=range(4),
            )

            for pyProfileData, mProfileData in getProfileData(rsk, mRSK):
                self.assertTrue(np.equal(pyProfileData, mProfileData).all())

            # ---- Test 3: shift conductivity channel from all downcasts with optimal lag from RSKcalculateCTlag.m ----
            # ---- lag = RSKcalculateCTlag(RSK_prof)
            # ---- RSKalignchannel(RSK_prof, 'channel', 'Conductivity', 'lag', lag)
            channelName = Conductivity.longName

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()
            lag = rsk.calculateCTlag()
            rsk.alignchannel(channel=channelName, lag=lag)

            mRSK = readMatlabFile("RSKalignchannel_test3.json")

            for pyProfileData, mProfileData in getProfileData(rsk, mRSK):
                self.assertTrue(np.equal(pyProfileData, mProfileData).all())

        # ----- Generic RSK tests -----
        for f in RSK_FILES_PROFILING:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                rsk.deriveseapressure()
                if rsk.channelexists(Conductivity):
                    lags = rsk.calculateCTlag(direction="both")
                    rsk.alignchannel(channel=Conductivity.longName, lag=lags)

    def test_correcthold(self):
        mRSK = readMatlabProfileDataWithNaN("RSKcorrecthold_nan_corrected.json")
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            pyholdpts = rsk.correcthold()  # , channels="conductivity")

            for pyData, mData in getProfileData(rsk, mRSK):
                mask = ~(np.isnan(mData) | np.isnan(pyData) | np.ma.getmask(pyData))
                self.assertGreater(len(pyData[mask]), 10000)
                self.assertTrue(np.allclose(pyData[mask], mData[mask], atol=1e-08, equal_nan=True))
            print("RSKcorrecthold with action nan passed")

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            pyholdpts = rsk.correcthold(action="interp")
            pyChannels = rsk.channelNames

            mChannels = ["Conductivity", "Temperature1", "Pressure", "Temperature2", "Dissolved O2"]
            pyProfileIndices = rsk.getprofilesindices()

            for chan in range(len(mChannels)):
                mRSK = readMatlabChannelDataByName(
                    readMatlabProfileDataWithNaN("RSKcorrecthold_corrected.json"), mChannels[chan]
                )
                for i in range(len(pyProfileIndices)):
                    mData = mRSK[i]
                    pyData = rsk.data[pyChannels[chan]][pyProfileIndices[i]]
                    mask = ~(np.isnan(mData) | np.isnan(pyData) | np.ma.getmask(pyData))
                    self.assertGreater(len(pyData[mask]), 1000)
                    self.assertTrue(
                        np.allclose(mData[mask], pyData[mask], atol=1e-6, equal_nan=True)
                    )
                print("pass (action interp)", pyChannels[chan])

        # ----- Generic RSK tests (profiling) -----
        for f in RSK_FILES_PROFILING:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                _ = rsk.correcthold(action="interp")

    def test_correctTM(self):
        mRSK = readMatlabFile("RSKcorrectTM.json")
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.correctTM(alpha=0.04, beta=0.1)
            for pyData, mData in getProfileData(rsk, mRSK, trim=2):
                mask = ~(np.isnan(mData) | np.isnan(pyData) | np.ma.getmask(pyData))
                self.assertTrue(np.allclose(pyData[mask], mData[mask], atol=1e-02, equal_nan=True))
        # Discrepancies come from the loop of profiles in pyRSK virsus casts in mRSK

        # ----- Matlab RSK tests -----
        mRSK = readMatlabChannelDataByName(readMatlabFile("RSKcorrectTM.json"), "Conductivity")
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()

            before = rsk.data[Conductivity.longName].copy()
            rsk.correctTM(alpha=0.04, beta=0.1)
            after = rsk.data[Conductivity.longName]

            pyProfileIndices = rsk.getprofilesindices()

            for i in range(len(pyProfileIndices)):
                mData = mRSK[i]
                pyData = after[pyProfileIndices[i]]
                pyDataBefore = before[pyProfileIndices[i]]

                # for ii in range(len(mData)):
                # print(mData[ii],pyData[ii],pyDataBefore[ii])

                mask = ~(
                    np.isnan(mData)
                    | np.isnan(pyData)  # (rsk.data[channelName])
                    | np.ma.getmask(pyData)  # (rsk.data[channelName])
                )
                self.assertGreater(len(pyData[mask]), 1000)
                self.assertTrue(np.allclose(mData[mask], pyData[mask], atol=1e-02, equal_nan=True))

        # ----- Generic RSK tests (profiling) -----
        for f in RSK_FILES_PROFILING:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                rsk.correctTM(alpha=0.04, beta=0.1)

    def test_correcttau(self):
        # ----- Matlab RSK tests -----
        # This function required the user to specify a channel
        channelName = DissolvedO2Saturation.longName

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.correcttau(channel=channelName, tauResponse=8)

            mRSK = readMatlabFile("RSKcorrecttau_corrected.json")

            for pyData, mData in getProfileData(rsk, mRSK):
                # self.assertTrue(np.equal(pyProfileData,mProfileData).all())
                self.assertTrue(np.allclose(pyData, mData, atol=1e-08, equal_nan=True))

        # ----- Generic RSK tests (profiling) -----
        channelName = Temperature.longName
        for f in RSK_FILES_PROFILING:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                rsk.correcttau(channel=channelName, tauResponse=2)

    def test_centrebursttimestamp(self):
        # ----- Matlab RSK tests -----
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            # The Matlab RSK does not contain wave/burst data, expect an error
            with self.assertRaises(TypeError):
                rsk.centrebursttimestamp()

        # ----- Golden RSK tests -----
        mRSK = readMatlabFile("RSKcentrebursttimestamp.json")
        mTSTAMP = np.array(mRSK["data"]["tstamp"])

        mAFTER = []
        for ii in range(len(mTSTAMP)):
            a = (
                datetime.fromordinal(int(mTSTAMP[ii]))
                + timedelta(days=mTSTAMP[ii] % 1)
                - timedelta(days=366)
            )
            # a = a.strftime("%Y-%m-%d %H:%M:%S.%f")#[:-3]
            mAFTER.append(np.datetime64(a, "ms").astype(np.uint64))

        with RSK(GOLDEN_RSK.as_posix()) as rsk:
            rsk.readdata()
            before = rsk.data["timestamp"].copy()
            rsk.centrebursttimestamp()
            pyAFTER = rsk.data["timestamp"].astype(np.uint64)
            self.assertTrue((abs(pyAFTER - mAFTER) <= 1).all())

    def test_trim(self):
        # ----- Matlab RSK tests -----
        # ----- Trim by timestamps -----
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()

            previous = rsk.data[Conductivity.longName].copy()
            trimmedIndices = rsk.trim(
                "time",
                (
                    np.datetime64("2021-10-30T05:21:25.750"),
                    np.datetime64("2021-10-30T05:27:29.125"),
                ),
                channels=Conductivity.longName,
                action="interp",
            )

            self.assertTrue(
                not np.equal(
                    previous[trimmedIndices], rsk.data[Conductivity.longName][trimmedIndices]
                ).all()
            )

            channels = [Conductivity.longName, Temperature.longName]

            trimmedIndices = rsk.trim(
                "time",
                (
                    np.datetime64("2021-10-30T05:21:20.750"),
                    np.datetime64("2021-10-30T05:27:31.125"),
                ),
                channels=channels,
                action="nan",
            )

            for channel in channels:
                self.assertTrue(np.isnan(rsk.data[channel][trimmedIndices]).all())

            originalSize = rsk.data.size
            trimmedIndices = rsk.trim(
                "time",
                (
                    np.datetime64("2021-10-30T05:21:20.750"),
                    np.datetime64("2021-10-30T05:27:31.125"),
                ),
                action="remove",
            )
            self.assertEqual(rsk.data.size, originalSize - len(trimmedIndices))

        # ----- Comparison test: trim by sea pressure -----
        # --- action = nan ---
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()
            mRSK = readMatlabProfileDataWithNaN("RSKtrim_corrected.json")
            rsk.trim(reference=SeaPressure.longName, range=[-1, 1], action="nan")
            for pyProfileData, mProfileData in getProfileData(rsk, mRSK):
                self.assertTrue(
                    np.allclose(pyProfileData, mProfileData, atol=1e-12, equal_nan=True)
                )
        # --- action = remove ---
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()
            mRSK = readMatlabProfileDataWithNaN("RSKtrim_corrected_remove.json")
            rsk.trim(reference=SeaPressure.longName, range=[-1, 1], action="remove")
            for pyProfileData, mProfileData in getProfileData(rsk, mRSK):
                self.assertTrue(
                    np.allclose(pyProfileData, mProfileData, atol=1e-12, equal_nan=True)
                )

    def test_binaverage(self):
        # ----- Matlab RSK tests -----

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()

            # Boundary must be of length of len(binSize) or len(binSize) + 1
            with self.assertRaises(ValueError):
                rsk.binaverage(binSize=[10.0, 20.0, 30.0], boundary=[10.0])

            # Only allow "up" or "down"
            with self.assertRaises(ValueError):
                rsk.binaverage(direction="both")

            # If no scheduleInfo, we can not determine sampling period. Expect error.
            if not rsk.scheduleInfo:
                with self.assertRaises(ValueError):
                    rsk.binaverage()

            # Default binBy is sea pressure, so expect error if missing
            if not rsk.channelexists(SeaPressure):
                with self.assertRaises(ValueError):
                    rsk.binaverage()
                # Now derive it so we can continue testing
                rsk.deriveseapressure()

            samplesinbin = rsk.binaverage()
            # TODO: sampleinbins match mRSK (manually check). However, there's a bug in mRSK that the output sampleinbin
            # only returns the last profile ones. mRSK needs to be fixed first.

        # ------ Comparison test1 ------
        # [rsk, samplesinbin] = RSKbinaverage(RSK, 'direction', 'down', 'binSize', [10 50], 'boundary', [10 50 300]);

        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()
            _ = rsk.binaverage(direction="down", binSize=[10, 50], boundary=[10, 50, 300])

            pyChannels = rsk.channelNames
            mChannels = [
                "Conductivity",
                "Temperature1",
                "Pressure",
                "Temperature2",
                "Dissolved O2",
                "Backscatter1",
                "Backscatter2",
                "Chlorophyll",
            ]
            pyProfileIndices = rsk.getprofilesindices()
            for i in range(len(mChannels)):
                mRSK = readMatlabChannelDataByName(
                    readMatlabFile("RSKbinaverage_corrected.json"), mChannels[i], direction="down"
                )
                for ii in range(len(pyProfileIndices)):
                    mData = mRSK[ii]
                    pyData = rsk.data[pyChannels[i]][pyProfileIndices[ii]]
                    self.assertTrue(np.allclose(pyData, mData, atol=1e-7, equal_nan=True))
                print("test1 pass: ", pyChannels[i])

        # ------ Comparison test2: binByTime ------
        # [rsk, samplesinbinbytime] = RSKbinaverage(RSK, 'binBy','Time', 'binSize', 3600);

        with RSK(BPR_RSK.as_posix()) as rsk:
            rsk.readdata()
            samplesinbin = rsk.binaverage(binBy="time", binSize=3600)

            pyChannels = rsk.channelNames
            mChannels = [
                "Temperature",
                "Barometer pressure period",
                "Barometer temperature period",
                "Period1",
                "Period2",
                "Period3",
                "Period4",
            ]
            for i in range(len(mChannels)):
                mData = readMatlabChannelDataByName(
                    readMatlabFile("RSKbinaverage_binbytime.json"), mChannels[i]
                )
                pyData = rsk.data[pyChannels[i]]
                self.assertTrue(np.allclose(pyData, mData, atol=1e-7, equal_nan=True))
                print("test2 pass: ", mChannels[i])

        # ----- Generic RSK tests (profiling) -----
        for f in RSK_FILES_PROFILING:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                rsk.deriveseapressure()
                _ = rsk.binaverage(direction="down", binSize=[10, 50], boundary=[10, 50, 300])

    def test_generate2D(self):
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            # rsk.deriveseapressure()
            # samplesinbin = rsk.binaverage()
            # img = rsk.generate2D()

        # TODO: how to compare against mValues?

    def test_smooth(self):
        # ----- MATLAB RSK tests -----

        # --- Test 1: profiling data, method: default boxcar
        # --- RSK = RSKreadprofiles(RSK);
        # --- rsk = RSKsmooth(RSK, 'channel', {'Temperature1', 'Conductivity'}, 'windowLength', 17);
        mRSK = readMatlabFile("RSKsmooth_profile_boxcar_corrected.json")
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            channelName = [Temperature.longName, Conductivity.longName]
            rsk.smooth(channels=channelName, windowLength=17)
            for pyProfileData, mProfileData in getProfileData(rsk, mRSK):
                self.assertTrue(np.allclose(pyProfileData, mProfileData, atol=1e-7, equal_nan=True))
        print("Test1 pass")

        # --- Test 2: profiling data, method: median
        # --- RSK = RSKreadprofiles(RSK);
        # --- rsk = RSKsmooth(RSK, 'channel', {'Temperature1', 'Conductivity'}, 'windowLength', 17,'filter','median');
        mRSK = readMatlabFile("RSKsmooth_profile_median_corrected.json")
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            channelName = [Temperature.longName, Conductivity.longName]
            rsk.smooth(channels=channelName, windowLength=17, filter="median")
            for pyProfileData, mProfileData in getProfileData(rsk, mRSK):
                self.assertTrue(np.allclose(pyProfileData, mProfileData, atol=1e-7, equal_nan=True))
        print("Test2 pass")

        # --- Test 3: profiling data, method: triangle
        # --- RSK = RSKreadprofiles(RSK);
        # --- rsk = RSKsmooth(RSK, 'channel', {'Temperature1', 'Conductivity'}, 'windowLength', 17,'filter','triangle');
        mRSK = readMatlabFile("RSKsmooth_profile_triangle_corrected.json")
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            channelName = [Temperature.longName, Conductivity.longName]
            rsk.smooth(channels=channelName, windowLength=17, filter="triangle")
            for pyProfileData, mProfileData in getProfileData(rsk, mRSK):
                self.assertTrue(np.allclose(pyProfileData, mProfileData, atol=1e-7, equal_nan=True))
        print("Test3 pass")

        # --- Test 4: moored data, method: default
        # --- RSK = RSKreaddata(RSK);
        # --- rsk = RSKsmooth(RSK, 'channel', {'Temperature','Conductivity','Pressure'}, 'windowLength', 1);
        channelName = [Temperature.longName, Conductivity.longName, Pressure.longName]
        with RSK(MATLAB_RSK_MOOR.as_posix()) as rsk:
            rsk.readdata()
            rsk.smooth(channels=channelName, windowLength=17)

            pyChannels = rsk.channelNames
            mChannels = [
                "Conductivity",
                "Temperature",
                "Pressure",
            ]
            for i in range(1):  # len(mChannels)):
                mData = readMatlabChannelDataByName(
                    readMatlabFile("RSKsmooth_moored_boxcar_corrected.json"), mChannels[i]
                )
                pyData = rsk.data[pyChannels[i]]
                # self.assertTrue(np.allclose(pyData[:-1], mData[:-1], atol=1e-8, equal_nan=True))
                self.assertTrue(np.allclose(pyData, mData, atol=1e-8, equal_nan=True))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                rsk.smooth(channels=rsk.channelNames[0])

    def test_despikes(self):

        # test1: action = nan
        # [RSK,spikepts] = RSKdespike(RSK,'action','nan','threshold',4,'windowLength',11,'channel','conductivity');
        channelName = Conductivity.longName
        mRSK = readMatlabChannelDataByName(
            readMatlabProfileDataWithNaN("RSKdespike_nan_corrected.json"), "Conductivity"
        )
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            spikepts = rsk.despike(action="nan", threshold=4, windowLength=11, channels=channelName)
            pyProfileIndices = rsk.getprofilesindices()
            for i in range(len(pyProfileIndices)):
                mData = mRSK[i]
                pyData = rsk.data[channelName][pyProfileIndices[i]]
                mask = ~(np.isnan(mData) | np.isnan(pyData) | np.ma.getmask(pyData))
                self.assertGreater(len(pyData[mask]), 1000)
                self.assertTrue(np.equal(mData[mask], pyData[mask]).all())

            # test2: action = replace
            # [RSK,~] = RSKdespike(RSK,'action','replace','threshold',4,'windowLength',11,'channel','conductivity');
        channelName = Conductivity.longName
        mRSK = readMatlabChannelDataByName(
            readMatlabProfileDataWithNaN("RSKdespike_replace_corrected.json"), "Conductivity"
        )
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            spikepts = rsk.despike(
                action="replace", threshold=4, windowLength=11, channels=channelName
            )
            pyProfileIndices = rsk.getprofilesindices()
            for i in range(len(pyProfileIndices)):
                mData = mRSK[i]
                pyData = rsk.data[channelName][pyProfileIndices[i]]
                self.assertTrue(np.allclose(mData, pyData, atol=1e-10, equal_nan=True))

            # test3: action = interp
            # [RSK,~] = RSKdespike(RSK,'action','interp','threshold',4,'windowLength',11,'channel','conductivity');
        channelName = Conductivity.longName
        mRSK = readMatlabChannelDataByName(
            readMatlabProfileDataWithNaN("RSKdespike_interp_corrected.json"), "Conductivity"
        )
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            spikepts = rsk.despike(
                action="interp", threshold=4, windowLength=11, channels=channelName
            )
            pyProfileIndices = rsk.getprofilesindices()
            for i in range(len(pyProfileIndices)):
                mData = mRSK[i]
                pyData = rsk.data[channelName][pyProfileIndices[i]]
                mask = ~(np.isnan(mData) | np.isnan(pyData) | np.ma.getmask(pyData))
                self.assertGreater(len(pyData[mask]), 1000)
                self.assertTrue(np.allclose(mData[mask], pyData[mask], atol=1e-10, equal_nan=True))

        # ----- Generic RSK tests -----
        for f in RSK_FILES:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                _ = rsk.despike(
                    channels=rsk.channelNames[0], action="interp", threshold=4, windowLength=11
                )

    def test_removeloops(self):
        # there's no channelIDs for derived channels in mRSK file, get errors when using getProfileData, so manually loop the channels
        with RSK(MATLAB_RSK.as_posix()) as rsk:
            rsk.readdata()
            rsk.deriveseapressure()
            rsk.derivedepth()
            rsk.derivevelocity()
            pyIdx = rsk.removeloops(threshold=0.1)

            pyChannels = rsk.channelNames
            mChannels = [
                "Conductivity",
                "Temperature1",
                "Pressure",
                "Temperature2",
                "Dissolved O2",
                "Backscatter1",
                "Backscatter2",
                "Chlorophyll",
            ]
            pyProfileIndices = rsk.getprofilesindices()

            for chan in range(len(mChannels)):
                mRSK = readMatlabChannelDataByName(
                    readMatlabProfileDataWithNaN("RSKremoveloops_corrected.json"), mChannels[chan]
                )
                for i in range(len(pyProfileIndices)):
                    mData = mRSK[i]
                    pyData = rsk.data[pyChannels[chan]][pyProfileIndices[i]]
                    mask = ~(np.isnan(mData) | np.isnan(pyData) | np.ma.getmask(pyData))
                    self.assertGreater(len(pyData[mask]), 1000)
                    self.assertTrue(
                        np.allclose(mData[mask], pyData[mask], atol=1e-10, equal_nan=True)
                    )
                print("pass ", pyChannels[chan])

        # ----- Generic RSK tests -----
        for f in RSK_FILES_PROFILING:
            with RSK(f.as_posix()) as rsk:
                rsk.readdata()
                rsk.deriveseapressure()
                rsk.derivedepth()
                rsk.derivevelocity()
                _ = rsk.removeloops(threshold=0.1)


if __name__ == "__main__":
    unittest.main()
