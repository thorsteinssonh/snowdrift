import logging

# output paremeter defs...
TYPE_OF_LEVEL=105
LEVEL=0
SNOW_COVER_AGE_PARAMETER=145
DRIFT_ACCUMULATION_PARAMETER=146
MOBILITY_INDEX_PARAMETER=147
SNOW_DRIFT_VALUE_PARAMETER=148

SNOW_COVER_LIMIT=1.0
SNOW_FALL_LIMIT=0.1

# tries to generate extra params from loaded data,
# required by snowdrift algorithm...
def calculateDeps(data):
    logging.info("calculating dependent parameters")
    # calculate snow fall (hourly rate), if not provided
    if ('snow' not in data) and ('snow-ac' in data):
        logging.info(" - calculating snow fall rate")
        unit = data['snow-ac']['unit'] + "/h"
        data['snow'] = {'times':[], 'values':[], 'unit':unit}


    # calculate wind from u/v if necessary,
    if 'wind' not in data and (('wind-u' in data) and ('wind-v' in data)):
        logging.info(" - calculating wind speed from u/v")
    else:
        raise ValueError("require 'wind' or 'wind-u/v' parameters for snow drift calculation")

    pass

def snowdrift(data):
    # calculate dependent parameters,
    # for snowdrift forecast calculation...
    # this is in-place on the input data dict
    calculateDeps(data)
    
    # now do snow drift algorithm...