#!/usr/bin/env python3
# Standard/external imports
from __future__ import annotations
from typing import *

if TYPE_CHECKING:
    from pyrsktools import RSK

_STATIC_TABLE_MAP: dict = {
    "dbInfo": {
        "columns": {
            "version": "VARCHAR(50)",
            "type": "VARCHAR(50)",
        },
        "constraints": [],
    },
    "instruments": {
        "columns": {
            "instrumentID": "INTEGER PRIMARY KEY",
            "serialID": "INTEGER",
            "model": "TEXT NOT NULL",
            "firmwareVersion": "TEXT",
            "firmwareType": "INTEGER",
            "partNumber": "TEXT",
        },
        "constraints": [],
    },
    "deployments": {
        "columns": {
            "deploymentID": "INTEGER PRIMARY KEY",
            "instrumentID": "INTEGER",
            "comment": "TEXT",
            "loggerStatus": "TEXT",
            "loggerTimeDrift": "long",
            "timeOfDownload": "long",
            "name": "TEXT",
            "sampleSize": "INTEGER",
            "dataStorage": "INTEGER DEFAULT 0",
            "loggerInitialStatus": "INTEGER DEFAULT 0",
        },
        "constraints": [],
    },
    "channels": {
        "columns": {
            "channelID": "INTEGER PRIMARY KEY",
            "shortName": "TEXT NOT NULL",
            "longName": "TEXT NOT NULL",
            "units": "TEXT",
            "longNamePlainText": "TEXT NOT NULL",
            "unitsPlainText": "TEXT",
            "isMeasured": "BOOLEAN",
            "isDerived": "BOOLEAN",
            "label": "TEXT NOT NULL DEFAULT ''",
            "feModuleType": "TEXT NOT NULL DEFAULT ''",
            "feModuleVersion": "NUMBER NOT NULL DEFAULT 0",
        },
        "constraints": [],
    },
    "epochs": {
        "columns": {
            "deploymentID": "INTEGER PRIMARY KEY",
            "startTime": "long",
            "endTime": "long",
        },
        "constraints": [],
    },
    "schedules": {
        "columns": {
            "scheduleID": "INTEGER PRIMARY KEY",
            "instrumentID": "INTEGER",
            "mode": "TEXT NOT NULL",
            "gate": "VARCHAR(512) NOT NULL",
        },
        "constraints": [],
    },
    "wave": {
        "columns": {
            "waveID": "INTEGER PRIMARY KEY",
            "scheduleID": "INTEGER NOT NULL",
            "samplingPeriod": "long NOT NULL",
            "repetitionPeriod": "long NOT NULL",
            "samplingCount": "INTEGER NOT NULL",
        },
        "constraints": [],
    },
    "continuous": {
        "columns": {
            "continuousID": "INTEGER PRIMARY KEY",
            "scheduleID": "INTEGER NOT NULL",
            "samplingPeriod": "long NOT NULL",
        },
        "constraints": [],
    },
    "burst": {
        "columns": {
            "burstID": "INTEGER PRIMARY KEY",
            "scheduleID": "INTEGER NOT NULL",
            "samplingPeriod": "long NOT NULL",
            "repetitionPeriod": "long NOT NULL",
            "samplingCount": "INTEGER NOT NULL",
        },
        "constraints": [],
    },
    "tide": {
        "columns": {
            "tideID": "INTEGER PRIMARY KEY",
            "scheduleID": "INTEGER NOT NULL",
            "samplingPeriod": "long NOT NULL",
            "repetitionPeriod": "long NOT NULL",
            "samplingCount": "INTEGER NOT NULL",
        },
        "constraints": [],
    },
    "average": {
        "columns": {
            "averageID": "INTEGER PRIMARY KEY",
            "scheduleID": "INTEGER NOT NULL",
            "samplingPeriod": "long NOT NULL",
            "repetitionPeriod": "long NOT NULL",
            "samplingCount": "INTEGER NOT NULL",
        },
        "constraints": [],
    },
    "directional": {
        "columns": {
            "directionalID": "INTEGER PRIMARY KEY",
            "scheduleID": "INTEGER NOT NULL",
            "direction": "VARCHAR(512) NOT NULL",
            "fastPeriod": "long NOT NULL",
            "slowPeriod": "long NOT NULL",
            "fastThreshold": "DOUBLE NOT NULL",
            "slowThreshold": "DOUBLE NOT NULL",
        },
        "constraints": [],
    },
    "region": {
        "columns": {
            "datasetID": "INTEGER NOT NULL",
            "regionID": "INTEGER PRIMARY KEY",
            "type": "VARCHAR(50)",
            "tstamp1": "LONG",
            "tstamp2": "LONG",
            "label": "VARCHAR(512)",
            "description": "TEXT",
            "collapsed": "BOOLEAN DEFAULT false",
        },
        "constraints": [],
    },
    "regionCal": {
        "columns": {
            "regionID": "INTEGER NOT NULL",
            "plateauSize": "INTEGER",
            "channelID": "INTEGER",
            "sourceID": "INTEGER",
        },
        "constraints": [
            "FOREIGN KEY(regionID) REFERENCES region(regionID) ON DELETE CASCADE ON UPDATE CASCADE",
            "FOREIGN KEY(channelID) REFERENCES channels(channelID) ON DELETE CASCADE ON UPDATE CASCADE",
        ],
    },
    "regionCast": {
        "columns": {
            "regionID": "INTEGER",
            "regionProfileID": "INTEGER",
            "type": "STRING",
        },
        "constraints": ["FOREIGN KEY(regionID) REFERENCES REGION(regionID) ON DELETE CASCADE"],
    },
    "regionComment": {
        "columns": {
            "regionID": "INTEGER",
            "content": "VARCHAR(1024)",
        },
        "constraints": ["FOREIGN KEY(regionID) REFERENCES REGION(regionID) ON DELETE CASCADE"],
    },
    "regionExclude": {
        "columns": {
            "regionID": "INTEGER",
            "enable": "BOOLEAN",
            "type": "STRING",
        },
        "constraints": ["FOREIGN KEY(regionID) REFERENCES REGION(regionID) ON DELETE CASCADE"],
    },
    "regionGeoData": {
        "columns": {
            "regionID": "INTEGER",
            "latitude": "DOUBLE",
            "longitude": "DOUBLE",
        },
        "constraints": ["FOREIGN KEY(regionID) REFERENCES REGION(regionID) ON DELETE CASCADE"],
    },
    "regionPlateau": {
        "columns": {
            "regionID": "INTEGER NOT NULL",
            "regionCalID": "INTEGER NOT NULL",
            "refValue": "DOUBLE",
            "refUnit": "VARCHAR(512)",
        },
        "constraints": [
            "FOREIGN KEY (regionID) REFERENCES region(regionID) ON DELETE CASCADE ON UPDATE CASCADE",
            "FOREIGN KEY (regionCalID) REFERENCES regionCal(regionID) ON DELETE CASCADE ON UPDATE CASCADE",
        ],
    },
    "regionProfile": {
        "columns": {
            "regionID": "INTEGER",
        },
        "constraints": ["FOREIGN KEY(regionID) REFERENCES REGION(regionID) ON DELETE CASCADE"],
    },
    "regionAtmosphere": {
        "columns": {
            "regionID": "INTEGER",
            "pressure": "DOUBLE",
            "unit": "STRING",
        },
        "constraints": ["FOREIGN KEY(regionID) REFERENCES REGION(regionID) ON DELETE CASCADE"],
    },
    "power": {
        "columns": {
            "deploymentID": "INTEGER NOT NULL REFERENCES deployments(deploymentID)",
            "internalBatteryType": "INTEGER NOT NULL DEFAULT 0",
            "externalBatteryType": "INTEGER NOT NULL DEFAULT 100",
            "internalBatteryCapacity": "REAL NOT NULL DEFAULT 0.0",
            "externalBatteryCapacity": "REAL NOT NULL DEFAULT 0.0",
            "internalEnergyUsed": "REAL NOT NULL DEFAULT 0.0",
            "externalEnergyUsed": "REAL NOT NULL DEFAULT 0.0",
            "e1": "REAL NOT NULL DEFAULT 0.0",
            "p1": "REAL NOT NULL DEFAULT 0.0",
            "p2": "REAL NOT NULL DEFAULT 0.0",
            "p3": "REAL NOT NULL DEFAULT 0.0",
            "powerSupplyPartNumber": "TEXT NOT NULL DEFAULT ''",
            "cellCount": "INTEGER NOT NULL DEFAULT 0",
        },
        "constraints": [],
    },
    "calibrations": {
        "columns": {
            "calibrationID": "INTEGER PRIMARY KEY",
            "channelOrder": "INTEGER",
            "instrumentID": "INTEGER",
            "type": "TEXT",
            "tstamp": "long",
            "equation": "TEXT",
        },
        "constraints": [],
    },
    "coefficients": {
        "columns": {
            "calibrationID": "INTEGER NOT NULL",
            "key": "TEXT",
            "value": "TEXT",
        },
        "constraints": ["PRIMARY KEY (calibrationID, key)"],
    },
    "parameters": {
        "columns": {
            "parameterID": "INTEGER PRIMARY KEY",
            "tstamp": "LONG",
        },
        "constraints": [],
    },
    "parameterKeys": {
        "columns": {
            "parameterID": "INTEGER NOT NULL",
            "key": "TEXT",
            "value": "TEXT",
        },
        "constraints": ["PRIMARY KEY (parameterID, key)"],
    },
    "appSettings": {
        "columns": {
            "deploymentID": "INTEGER PRIMARY KEY",
            "ruskinVersion": "TEXT",
        },
        "constraints": [],
    },
    "ranging": {
        "columns": {
            "instrumentID": "INTEGER",
            "channelID": "INTEGER",
            "channelOrder": "INTEGER",
            "mode": "VARCHAR(512)",
            "gain": "FLOAT",
            "availableGains": "VARCHAR(512)",
        },
        "constraints": ["PRIMARY KEY (instrumentID, channelID, channelOrder)"],
    },
    "instrumentSensors": {
        "columns": {
            "instrumentID": "INTEGER",
            "sensorID": "INTEGER",
            "channelOrder": "INTEGER",
            "serialID": "INTEGER",
            "details": "VARCHAR(512)",
        },
        "constraints": [],
    },
    "instrumentChannels": {
        "columns": {
            "instrumentID": "INTEGER",
            "channelID": "INTEGER",
            "channelOrder": "INTEGER",
            "channelStatus": "INTEGER",
        },
        "constraints": ["PRIMARY KEY (instrumentID, channelID, channelOrder)"],
    },
    "data": {
        "columns": {
            "tstamp": "BIGINT",
        },
        "constraints": [],
    },
    "burstData": {
        "columns": {
            "tstamp": "BIGINT",
        },
        "constraints": [],
    },
}


def create_rsk_table_map(rsk: RSK) -> dict:
    tableMap = _STATIC_TABLE_MAP

    # Generate the columns names for the data tables.
    # The name of each of these columns should match with
    # those in the "channels" table, henece why we iterate
    # through them all below.
    for cName in rsk.channelNames:
        matched = False
        for c in rsk.channels:
            if cName == c.longName:
                tableMap["data"]["columns"][f"channel{str(c.channelID).zfill(2)}"] = "DOUBLE"
                matched = True
                break

        if not matched:
            raise ValueError(
                f"Channel {cName} in RSK.data is missing a corresponding entry in RSK.channels"
            )

    assert 1 + len(rsk.channelNames) == len(tableMap["data"]["columns"])

    # NOTE: this must be changed to processedData<Suffix>, processedChannels<Suffix> and processedInfo<Suffix>
    # when the new RSK format is released (and supported by pyRSKtools).
    for cName in rsk.processedChannelNames:
        matched = False
        for c in rsk.channels:
            if cName == c.longName:
                tableMap["burstData"]["columns"][f"channel{str(c.channelID).zfill(2)}"] = "DOUBLE"
                matched = True
                break

        if not matched:
            raise ValueError(
                f"Channel {cName} in RSK.processedData is missing a corresponding entry in RSK.channels"
            )

    assert 1 + len(rsk.processedChannelNames) == len(tableMap["burstData"]["columns"].keys())

    return tableMap
