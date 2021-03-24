import logging
from .collect_data import summary, check_consistency

# output paremeter defs...
TYPE_OF_LEVEL=105
LEVEL=0
SNOW_COVER_AGE_PARAMETER=145
DRIFT_ACCUMULATION_PARAMETER=146
MOBILITY_INDEX_PARAMETER=147
SNOW_DRIFT_VALUE_PARAMETER=148

SNOW_COVER_LIMIT=1.0
SNOW_FALL_LIMIT=0.1

# the main snow drift algorithm on loaded data
def snowdrift(data):
    # calculate dependent parameters,
    # for snowdrift forecast calculation...
    # this is in-place on the input data dict
    calculateDeps(data)
    
    # now do snow drift algorithm...

    # return results
    return data

# tries to generate extra params from loaded data,
# that are required by snowdrift algorithm...
def calculateDeps(data):
    logging.info("calculating dependent parameters")

    # snow fall rate if not provided,
    calculate_snowfall(data)
    # wind from wind u/v if not provided,
    calculate_wind(data)
    # calculate snow age,
    calculate_snow_age(data)
 
    # print post deps data summary
    summary(data)
    # consistency checks
    check_consistency(data)


def calculate_drift_accumulation(data):
    pass

# calculate snow fall (hourly rate), if not provided
def calculate_snowfall(data):
    if ('snowfall' not in data) and ('snowac' in data):
        logging.info(" - calculating snow fall rate")
        unit = data['snowac']['unit'] + "/h"
        data['snowfall'] = {'times':[], 'values':[], 'unit':unit}
        snowac = data['snowac']['values']
        times = data['snowac']['times']
        n = len(times)
        snowfall = data['snowfall']['values']
        snowfalltimes = data['snowfall']['times']

        # first snow step...
        snowfall.append( snowac[0]*0.0 ) # zeroed first step
        snowfalltimes.append( times[0] )
        # rest are diff...
        for i in range(1, n):
            # hourly snowfall, so get time step...
            dtHours = (times[i] - times[i-1]).total_seconds()/3600.0
            dSnow = (snowac[i] -  snowac[i-1])/dtHours
            snowfall.append(dSnow)
            snowfalltimes.append(times[i])


# calculate wind from u/v if necessary,
def calculate_wind(data):
    if 'wind' not in data and (('wind-u' in data) and ('wind-v' in data)):
        logging.info(" - calculating wind speed from u/v")
        unit = data['wind-u']['unit']
        data['wind'] = {'times':[], 'values':[], 'unit':unit}
        windu = data['wind-u']['values']
        windv = data['wind-v']['values']
        times = data['wind-u']['times']
        wind = data['wind']['values']
        windtimes = data['wind']['times']
        n = len(times)
        for i in range(n):
            u = windu[i]
            v = windv[i]
            t = times[i]
            spd = (u**2 + v**2)**0.5
            wind.append(spd)
            windtimes.append(t)
        # can delete u/v wind after wind calculation
        del data['wind-u']
        del data['wind-v']
    else:
        raise ValueError("require 'wind' or 'wind-u/v' parameters for snow drift calculation")

def calculate_snow_age(data):
    logging.info(" - calculating snow age")
    unit = "hours"
    data['snowage'] = {'times':[], 'values':[], 'unit':unit}
    snowage = data['snowage']['values']
    snowagetimes = data['snowage']['times']
    # input
    snowfall = data['snowfall']['values']
    snowground = None
    if 'snowground' in data:
        snowground = data['snowground']['values']
    times = data['snowfall']['times']
    n = len(times)

    # here we set the first age step,
    # TODO: should be loaded from prev forecast
    # now just start from zero...
    isc = is_snow_covered(data, 0)
    age = snowfall[0]*0.0
    age[~isc] = -1.0
    snowage.append(age)
    snowagetimes.append(times[0])
    # loop through rest of steps,
    for i in range(1, n):
        # create age holder, zero values initally
        age = snowfall[i]*0.0
        isc = is_snow_covered(data, i)
        new = is_new_snow(data, i)
        melting = is_melting_temp(data, i)

        # no snow cover, set age to -1
        age[~isc] = -1.0

        # add upp times from previous step,
        # for areas that are snow covered
        dtHours = (times[i] - times[i-1]).total_seconds()/3600.0
        age[isc] = snowage[i-1][isc] + dtHours

        # if new snow, set 0 hours age on those areas
        age[new] = 0.0

        # temperature affects new snow cover here...
        age[melting] = 0.0
        age[~isc] = -1.0

        # snowground if provided,
        if snowground:
            sg = snowground[i] > 0.1
            age[~sg] = -1

        # append data,
        snowage.append(age)
        snowagetimes.append(times[i])

    ## negative ones ...
    #cdo setrtoc,-10.0,10.0,-1.0 is_snow_covered.${i_str}.grb _neg_ones.grb
    ## inv snow mask ...
    #cdo ltc,1.0 is_snow_covered.${i_str}.grb _inv_is_snow_covered.grb
    ## inv new snow mask ...
    #cdo ltc,1.0 is_new_snow.${i_str}.grb _inv_is_new_snow.${i_str}.grb
    #
    #if [ $i -lt 1 ]; then
	#if [ -f ${forecast_dir}/harmonie_${prev_run_time_str}.06 ]; then
	#    cat>snow_age.filter<<EOF
    ##if ( indicatorOfTypeOfLevel == 105 && indicatorOfParameter == ${SNOW_COVER_AGE_PARAMETER} )
    #{
    #    write "snow_cover_age.${i_str}.grb";
    #}
    #EOF
	#    grib_filter snow_age.filter ${forecast_dir}/harmonie_${prev_run_time_str}.06
	#    rm snow_age.filter
	#    if [ ! -f snow_cover_age.${i_str}.grb ]; then
    #            # initialize snow age ( fill with -1 where no snow, and 0 where snow )
	#        cdo mul _inv_is_snow_covered.grb _neg_ones.grb snow_cover_age.${i_str}.grb
	#    fi
	#else
    #        # initialize snow age ( fill with -1 where no snow, and 0 where snow )
	#    cdo mul _inv_is_snow_covered.grb _neg_ones.grb snow_cover_age.${i_str}.grb
	#fi
    #else
	## age up snow by one day
	#cdo add snow_cover_age.${im1_str}.grb is_snow_covered.${i_str}.grb _aged.grb
	#replace_values is_snow_covered.${i_str}.grb snow_cover_age.${im1_str}.grb _aged.grb _tmp1.grb#
    #
	# set new snow area back to 0
	#cdo mul _inv_is_new_snow.${i_str}.grb _tmp1.grb _tmp2.grb
    #
	## set snow free area back to -1
	#replace_values _inv_is_snow_covered.grb _tmp2.grb _neg_ones.grb _tmp3.grb
    #
	## deliver
	#mv _tmp3.grb snow_cover_age.${i_str}.grb
	#### this above stuff is broken, need to add and reset snow age properly.
    #fi


# calculate boolean if new snowfall in this step,
def is_new_snow(data, i):
    return data['snowfall']['values'][i] > SNOW_FALL_LIMIT

# calculate boolean if ground snow covered,
def is_snow_covered(data, i):
    return data['snowac']['values'][i] > SNOW_COVER_LIMIT

# calculate boolean for top snow is melting
def is_melting_temp(data, i):
    return data['temp']['values'][i] > 0.0

