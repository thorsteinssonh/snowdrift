import pygrib

TYPE_OF_LEVEL=105
LEVEL=0
SNOW_COVER_AGE_PARAMETER=145
DRIFT_ACCUMULATION_PARAMETER=146
MOBILITY_INDEX_PARAMETER=147
SNOW_DRIFT_VALUE_PARAMETER=148

# Saves snowdrift parameters to a new grib file,
# appending each message.
# Requires a template message from source forecast
# in oreder to replace values and write in compatible
# GRIB formatting to the source.
save_grib(data, filename, template_msg):
    pass