#!/usr/bin/env python3
"""
Tests for pyRSKtools internally used reader classes.
"""
# Standard/external imports
import unittest
import sqlite3

# Module imports
from pyrsktools import RSK, utils
from pyrsktools.readers import load_reader
from common import RSK_FILES, GOLDEN_RSK, GOLDEN_RSK_TYPE, GOLDEN_RSK_VERSION


class TestRead(unittest.TestCase):
    def test_reader(self):
        # Open the RSK (sqlite3) file
        db = sqlite3.connect(f"file:{GOLDEN_RSK.as_posix()}?mode=ro", uri=True)
        dbInfo, reader = load_reader(db)
        self.assertEqual(dbInfo.type, "EPdesktop")
        # List of tuples containing known longName and _dbName
        names = [
            ("conductivity", "Conductivity"),
            ("temperature", "Temperature"),
            ("pressure", "Pressure"),
            ("sea_pressure", "Sea pressure"),
            ("depth", "Depth"),
            ("salinity", "Salinity"),
            ("speed_of_sound", "Speed of sound"),
            ("specific_conductivity", "Specific conductivity"),
            ("tidal_slope", "Tidal slope"),
            ("significant_wave_height", "Significant wave height"),
            ("significant_wave_period", "Significant wave period"),
            ("one_tenth_wave_height", "1/10 wave height"),
            ("one_tenth_wave_period", "1/10 wave period"),
            ("maximum_wave_height", "Maximum wave height"),
            ("maximum_wave_period", "Maximum wave period"),
            ("average_wave_height", "Average wave height"),
            ("average_wave_period", "Average wave period"),
            ("wave_energy", "Wave energy"),
        ]
        for i, channel in enumerate(reader.channels()):
            self.assertEqual(channel.longName, names[i][0])
            self.assertEqual(channel._dbName, names[i][1])

        db.close()

    def test_full_reader(self):
        pass

    def test_epdesktop_reader(self):
        pass


if __name__ == "__main__":
    unittest.main()
