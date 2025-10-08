#!/usr/bin/env python3
# Standard/external imports
import unittest
import numpy as np

# Module imports
from pyrsktools import RSK, utils
from common import RSK_FILES, GOLDEN_RSK, GOLDEN_RSK_TYPE, GOLDEN_RSK_VERSION


class TestUtils(unittest.TestCase):
    def test_semver2int(self):
        # This test assumes each semver str in this list is greater
        # than all the others before it.
        semverStrs = ["1.2.3", "1.18.17", "2.16.0"]
        semverInts = [utils.semver2int(s) for s in semverStrs]

        for i in range(len(semverInts)):
            for j in reversed(range(-len(semverInts) + i + 1, 0)):
                self.assertLess(semverInts[i], semverInts[j])

    def test_formatchannelname(self):
        strings = [
            "Conductivity",
            "Speed of sound",
            "1/10 wave height",
            "Dissolved O₂",
            "2 1/10 wave height",
            "2 Dissolved O₂",
        ]
        expected = [
            "conductivity",
            "speed_of_sound",
            "one_tenth_wave_height",
            "dissolved_o2",
            "x2_one_tenth_wave_height",
            "x2_dissolved_o2",
        ]
        self.assertEqual(len(strings), len(expected))
        for i in range(len(strings)):
            formatted = utils.formatchannelname(strings[i])
            self.assertEqual(formatted, expected[i])

    def test_intoarray(self):
        given = [[1, 2, 3], 4, [1.2, None], None, range(0, 3)]
        expected = [
            np.array([1, 2, 3], dtype="double"),
            np.array([4], dtype="double"),
            np.array([1.2, None], dtype="double"),
            np.array([np.nan]),
            np.array(list(range(0, 3)), dtype="double"),
        ]
        for i in range(len(given)):
            g = utils.intoarray(given[i])
            self.assertEqual(type(g), type(expected[i]))
            self.assertTrue(np.allclose(g, expected[i], equal_nan=True))

        with self.assertRaises(ValueError):
            utils.intoarray(["not", "a", "float"])
            utils.intoarray("notafloat")

    def test_mirrorpad(self):
        a = np.array([1, 2, 3])

        with self.assertRaises(ValueError):
            utils.mirrorpad(a, len(a) + 1)

        b = utils.mirrorpad(a, 2)
        self.assertTrue(np.array_equal(b, [2, 1, 1, 2, 3, 3, 2]))

    def test_nanpad(self):
        a = np.array([1, 2, 3])

        with self.assertRaises(ValueError):
            utils.nanpad(a, len(a) + 1)

        b = utils.nanpad(a, 2)
        self.assertTrue(
            np.array_equal(
                b,
                [np.nan, np.nan, 1, 2, 3, np.nan, np.nan],
                equal_nan=True,
            )
        )

    def test_zeroorderholdpad(self):
        a = np.array([1, 2, 3])

        with self.assertRaises(ValueError):
            utils.zeroorderholdpad(a, len(a) + 1)

        b = utils.zeroorderholdpad(a, 2)
        self.assertTrue(np.array_equal(b, [1, 1, 1, 2, 3, 3, 3]))

    def test_padseries(self):
        a = np.array([1, 2, 3])
        padSize = 2
        out = [
            [2, 1, 1, 2, 3, 3, 2],
            [np.nan, np.nan, 1, 2, 3, np.nan, np.nan],
            [1, 1, 1, 2, 3, 3, 3],
        ]
        edge = ["mirror", "nan", "zeroorderhold"]

        for i in range(len(out)):
            with self.assertRaises(ValueError):
                utils.padseries(a, len(a) + 1, edge[i])

            b = utils.padseries(a, padSize, edge[i])
            self.assertTrue(np.array_equal(b, out[i], equal_nan=True))

    def test_runavg(self):
        a = np.array([1, 2, 1, 2, 1, 2])
        out = [1.33333333, 1.33333333, 1.66666667, 1.33333333, 1.66666667, 1.66666667]
        windowLenth = 3

        with self.assertRaises(ValueError):
            utils.runavg(a, windowLenth + 1)  # Must be odd, so this should raise error

        b = utils.runavg(a, windowLenth)
        self.assertTrue(np.allclose(b, out))

    def test_lagave(self):
        inArray = np.array([1, 2, 3, 4, 5, 6])
        expected = np.array([np.nan, 1.5, 2.5, 3.5, 4.5, 5.5])
        outArray = utils.lagave(inArray)
        self.assertTrue(np.allclose(outArray, expected, equal_nan=True))

    def test_shiftarray(self):
        inArray = np.array([1, 2, 3, 4, 5, 6])

        expected = np.array([np.nan, np.nan, 1, 2, 3, 4])
        outArray = utils.shiftarray(inArray, 2, "nan")
        self.assertTrue(np.allclose(outArray, expected, equal_nan=True))

        expected = np.array([3, 4, 5, 6, np.nan, np.nan])
        outArray = utils.shiftarray(inArray, -2, "nan")
        self.assertTrue(np.allclose(outArray, expected, equal_nan=True))


if __name__ == "__main__":
    unittest.main()
