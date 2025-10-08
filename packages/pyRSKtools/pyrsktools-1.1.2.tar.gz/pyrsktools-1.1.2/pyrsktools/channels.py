#!/usr/bin/env python3
# Standard/external imports
from dataclasses import dataclass

# Module imports
from pyrsktools.datatypes import Channel

# ------- Basic dataclasses containing information of channels we manually must reference or derive -------
# Reference: https://docs.rbr-global.com/L3commandreference/supported-channel-types
# NOTE: channelID will be None for each of the below. Use the Channel.withnewid() instance
# method to create a new instance of these with a given ID, e.g., Conductivity.withnewid(1).

Conductivity = Channel(
    shortName="cond09",
    longName="conductivity",
    units="mS/cm",
    _dbName="Conductivity",
)
Temperature = Channel(
    shortName="temp09",
    longName="temperature",
    units="°C",
    _dbName="Temperature",
)
Pressure = Channel(
    shortName="pres24",
    longName="pressure",
    units="dbar",
    _dbName="Pressure",
)
SeaPressure = Channel(
    shortName="pres08",
    longName="sea_pressure",
    units="dbar",
    _dbName="Sea pressure",
)
PressureDrift = Channel(
    shortName="drft00",
    longName="pressure_drift",
    units="dbar",
    _dbName="Pressure drift",
)
BprPressure = Channel(
    shortName="bpr_08",
    longName="bpr_pressure",
    units="dbar",
    _dbName="BPR pressure",
)
BprCorrectedPressure = Channel(
    shortName="dbpr00",
    longName="bpr_corrected_pressure",
    units="dbar",
    _dbName="BPR corrected pressure",
)
BarometerPressure = Channel(
    shortName="baro02",
    longName="barometer_pressure",
    units="dbar",
    _dbName="Barometer pressure",
)
BprTemperature = Channel(
    shortName="bpr_09",
    longName="bpr_temperature",
    units="°C",
    _dbName="BPR temperature",
)
BarometerTemperature = Channel(
    shortName="baro03",
    longName="barometer_temperature",
    units="°C",
    _dbName="Barometer temperature",
)
Salinity = Channel(
    shortName="sal_00",
    longName="salinity",
    units="PSU",
    _dbName="Salinity",
)
Depth = Channel(
    shortName="dpth01",
    longName="depth",
    units="m",
    _dbName="Depth",
)
Velocity = Channel(
    shortName="pvel00",
    longName="velocity",
    units="m/s",
    _dbName="Velocity",
)
SpecificConductivity = Channel(
    shortName="scon00",
    longName="specific_conductivity",
    units="µS/cm",
    _dbName="Specific conductivity",
)
DissolvedO2Concentration = Channel(
    shortName="doxy27",
    longName="dissolved_o2_concentration",
    units="µmol/l",
    _dbName="Dissolved O₂ concentration",
)
DissolvedO2Saturation = Channel(
    shortName="doxy13",
    longName="dissolved_o2_saturation",
    units="%",
    _dbName="Dissolved O₂ saturation",
)
BuoyancyFrequencySquared = Channel(
    shortName="buoy00",
    longName="buoyancy_frequency_squared",
    units="1/s²",
    _dbName="Buoyancy Frequency Squared",
)
Stability = Channel(
    shortName="stbl00",
    longName="stability",
    units="1/m",
    _dbName="Stability",
)
DensityAnomaly = Channel(
    shortName="dden00",
    longName="density_anomaly",
    units="kg/m³",
    _dbName="Density anomaly",
)
AbsoluteSalinity = Channel(
    shortName="sal_02",
    longName="absolute_salinity",
    units="g/kg",
    _dbName="Absolute salinity",
)
PotentialTemperature = Channel(
    shortName="temp49",
    longName="potential_temperature",
    units="°C",
    _dbName="Potential temperature",
)
SpeedOfSound = Channel(
    shortName="sos_00",
    longName="speed_of_sound",
    units="m/s",
    _dbName="Speed of Sound",
)
Chlorophyll = Channel(
    shortName="fluo33",
    longName="chlorophyll",
    units="counts",
    _dbName="Chlorophyll",
)
Backscatter = Channel(
    shortName="turb04",
    longName="backscatter",
    units="counts",
    _dbName="Backscatter",
)
Phycoerythrin = Channel(
    shortName="fluo35",
    longName="phycoerythrin",
    units="counts",
    _dbName="Phycoerythrin",
)
AccelerationX = Channel(
    shortName="accx00",
    longName="x_axis_acceleration",
    units="m/s²",
    _dbName="X axis acceleration",
)
AccelerationY = Channel(
    shortName="accy00",
    longName="y_axis_acceleration",
    units="m/s²",
    _dbName="Y axis acceleration",
)
AccelerationZ = Channel(
    shortName="accz00",
    longName="z_axis_acceleration",
    units="m/s²",
    _dbName="Z axis acceleration",
)
AccelerometerTemperature = Channel(
    shortName="temp41",
    longName="accelerometer_temperature",
    units="°C",
    _dbName="Accelerometer temperature",
)
