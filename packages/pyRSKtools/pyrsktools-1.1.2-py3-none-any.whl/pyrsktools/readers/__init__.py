#!/usr/bin/env python3
# Standard/external imports
import sqlite3
from typing import Tuple, Union

# Module imports (exports)
from .reader import Reader
from .rskfull import RSKFullReader
from .rskepdesktop import RSKEPDesktopReader
from pyrsktools.datatypes import DbInfo


def load_reader(db: sqlite3.Connection) -> Tuple[DbInfo, Reader]:
    cur = db.cursor()
    # Get version information
    cur.execute("SELECT version, type FROM dbInfo ORDER BY _rowid_ DESC LIMIT 1")
    r = cur.fetchone()

    dbInfo = DbInfo(version=r[0], type=r[1])

    reader: Union[RSKFullReader, RSKEPDesktopReader] = None
    # Create schema depending on type
    if dbInfo.type == RSKFullReader.TYPE:
        reader = RSKFullReader(db, dbInfo.version)
    elif dbInfo.type == RSKEPDesktopReader.TYPE:
        reader = RSKEPDesktopReader(db, dbInfo.version)
    elif dbInfo.type == "cervello":
        raise TypeError(
            f"Unsupported RSK type: {dbInfo.type}. Please open the file with Ruskin first."
        )
    else:
        raise TypeError(f"Unsupported RSK type: {dbInfo.type}")

    return dbInfo, reader
