#!/usr/bin/env python3
# Standard/external imports
from typing import *
import dataclasses


# Module imports
from pyrsktools.readers import Reader
from pyrsktools.utils import semver2int, rsktime2datetime
from pyrsktools.datatypes import *


class RSKFullReader(Reader):
    TYPE: str = "full"
    MIN_SUPPORTED_SEMVER: str = "2.0.0"
    MAX_SUPPORTED_SEMVER: str = "2.18.2"

    def regions(
        self,
    ) -> List[
        Union[
            RegionCal,
            RegionCast,
            RegionComment,
            RegionExclude,
            RegionGeoData,
            RegionPlateau,
            RegionProfile,
            RegionAtmosphere,
        ]
    ]:
        results = []
        parentTable = "region"

        for childClass, mapping in self.REGION_TYPE_MAPPING.items():
            childTable = mapping["table"]
            regionType = mapping["type"]

            columns: Set[str] = {field.name for field in dataclasses.fields(childClass)}
            columns.discard("type")
            columns.add(f"{parentTable}.type")
            columns.discard("regionID")
            columns.add(f"{parentTable}.regionID")
            if regionType == "CAST" or regionType == "EXCLUSION":
                columns.discard("regionType")
                columns.add(f"{childTable}.type as regionType")

            if self.version <= semver2int("2.0.0"):
                columns.discard("collapsed")

            for row in self._query(
                parentTable,
                columns=columns,
                outerJoin=(childTable, "regionID"),
                where=f'{parentTable}.type="{regionType}"',
            ):
                instance = childClass(
                    **{
                        field: row[field]
                        if field != "tstamp1" and field != "tstamp2"
                        else rsktime2datetime(row[field])
                        for field in row.keys()
                    }
                )
                results.append(instance)

        return results

    def calibrations(self: Reader) -> List[Calibration]:
        datatype, table = Calibration, "calibrations"
        coefTable = "coefficients"

        # NOTE: below is a modified version of self._createDatatypesFromQuery()
        results = []
        datatypeFields: dict = {}
        commonFields: Set[str] = set()

        for row in self._query(table):
            if not datatypeFields:
                datatypeFields = {field.name: field.type for field in dataclasses.fields(datatype)}
                commonFields = set(row.keys()).intersection(datatypeFields.keys())

            fieldsDict = {
                field: row[field]
                if datatypeFields[field] != "datetime64"
                else rsktime2datetime(row[field])
                for field in commonFields
            }

            # In full RSKs, there are a variable number of coefficients related
            # to each calibration row, however they are in a separate "coefficients" table.
            # The below grabs all the coefficients from that separate table and merges them
            # into our datatype instance.
            calibrationID = fieldsDict["calibrationID"]

            # For dictionaries below, key is coefficient number and value are...coef value.
            fieldsDict["c"], fieldsDict["x"], fieldsDict["n"] = {}, {}, {}
            for cRow in self._query(
                coefTable, where=f"calibrationID = {calibrationID}", orderByAsc="key"
            ):
                coefKey = int(cRow["key"][1:])
                coefValue = np.nan if cRow["value"] is None else cRow["value"]

                if cRow["key"].startswith("c"):
                    fieldsDict["c"][coefKey] = float(coefValue)
                elif cRow["key"].startswith("x"):
                    fieldsDict["x"][coefKey] = float(coefValue)
                elif cRow["key"].startswith("n"):
                    fieldsDict["n"][coefKey] = int(coefValue)
                else:
                    raise ValueError(
                        f"Unsupported coefficient type found in '{coefTable}' table: {coefKey}"
                    )

            results.append(datatype(**fieldsDict))

        return results
