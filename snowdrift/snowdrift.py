import logging
from .collect_data import summary, check_consistency

# Default model thresholds
SNOW_COVER_LIMIT=1.0
SNOW_FALL_LIMIT=0.1


# the main snow drift algorithm on loaded data
def snowdrift(data):
    # calculate dependent parameters,
    # for snowdrift forecast calculation...
    # this is in-place on the input data dict
    calculateDeps(data)
    
    # do snow drift algorithm, in steps,
    # because SA,DA,MI and SDV are interdependent calculations,
    logging.info("snow drift algorithm")
    for i in range(nsteps(data)):
        logging.info("Drift calculation step %d"%i)
        calculate_snow_cover_age(data, i)
        calculate_drift_accumulation(data, i)
        calculate_mobility_index(data, i)
        calculate_drift(data, i)


    summary(data)

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
 
    # print post deps data summary
    summary(data)
    # consistency checks
    check_consistency(data)

# The drift value calculated here
def calculate_drift(data, i):
    logging.info(" - calculating snow mobility %d"%i)

    if i == 0:
        data['drift'] = {'times':[], 'values':[], 'unit': ""}

    drift = data['drift']['values']
    drifttimes = data['drift']['times']
    
    t = get_times(data)[i]
    wind = data['wind']['values'][i]
    mi = data['mobility']['values'][i]

    d = mi*(wind**3.0)/1728.0

    # set to zero if wind < 6.0
    d[wind<6.0] = 0.0

    # set snow free areas to -1
    # mainly just for better plotting
    isc = is_snow_covered(data, i)
    d[~isc] = -1

    # append
    drift.append(d)
    drifttimes.append(t)

# Mobility index/factor is 1 after new snowfall, but
# decreases...
def calculate_mobility_index(data, i):
    logging.info(" - calculating snow mobility %d"%i)

    # input
    times = get_times(data)

    if i == 0:
        data['mobility'] = {'times':[], 'values':[], 'unit': ""}

    mobility = data['mobility']['values']
    mobilitytimes = data['mobility']['times']

    if i == 0:
        # TODO: get previous FC mobility
        # if no prev run data, initialize mobility index (with zeros)
        mi = new_array(data)
        mobility.append(mi)
        mobilitytimes.append(times[0])
    else:
        mi = mobility[i-1].copy() # make copy of prev step

        # if new snow, reset mobility to 1.0
        new = is_new_snow(data, i)
        mi[new] = 1.0

        # apply snow cover age reduction...
        age = data['snowage']['values'][i]
        mi[ (mi == 1.0)&(age >= 24) ] = 0.6

        # apply drift accumulation reduction,
        dacc = data['driftacc']['values'][i]
        mi[ dacc >= 2.0 ] = 0.6   # [2.0 6.0] range
        mi[ dacc > 6.0 ] = 0.3    # > 6.0 range

        # melting and snow cover nulling,
        melting = is_melting_temp(data, i)
        isc = is_snow_covered(data, i)
        mi[melting] = 0.0
        mi[~isc] = 0.0

        # append,
        mobility.append(mi)
        mobilitytimes.append(times[i])

# Drift accumulation keeps track of quantity of accumulated drifting
# DA increases by SDValue when wind[i-1] >= 6 m/s.
# reset accumulation to 0 when new snow
def calculate_drift_accumulation(data, i):
    logging.info(" - calculating drift accumulation %d"%i)

    # input
    snowfall = data['snowfall']['values']
    times = get_times(data)

    if i == 0:
        data['driftacc'] = {'times':[], 'values':[], 'unit':''}

    driftacc = data['driftacc']['values']
    driftacctimes = data['driftacc']['times']

    if i == 0:
        # here we set the first step,
        # zero by default...
        # TODO: should be loaded from prev forecast
        dacc = new_array(data)
        driftacc.append(dacc)
        driftacctimes.append(times[0])
    else:
        # prev wind, drift, drif accumulation
        pWind = data['wind']['values'][i-1]
        pDrift = data['drift']['values'][i-1]
        pDacc = data['driftacc']['values'][i-1]
        # accumulate drift with wind > 6.0
        dacc = pDacc.copy() # copy from previous
        windy = pWind > 6.0
        dacc[windy] = pDacc[windy] + pDrift[windy]
        # reset accumulation when new snow,
        new = is_new_snow(data, i)
        dacc[new] = 0.0
        # append result,
        driftacc.append(dacc)
        driftacctimes.append(times[i])

# Rules for aging:
# if no snow cover -> -1  # no age value
# if new snow fall -> 0 age
# else age snow by 1 fc time step (in hours)
#
# NOTE: snow cover age, does not keep track of meltin
#       this is done in mobility index,
#       i.e. melting, will turn off mobility of the top layer
def calculate_snow_cover_age(data, i):
    logging.info(" - calculating snow age %d"%i)

    times = get_times(data)

    if i == 0:
        unit = "hours"
        data['snowage'] = {'times':[], 'values':[], 'unit':unit}

    snowage = data['snowage']['values']
    snowagetimes = data['snowage']['times']

    if i == 0:
        # here we set the first age step,
        # TODO: should be loaded from prev forecast
        # now just start from zero...
        isc = is_snow_covered(data, 0)
        age = new_array(data) - 1.0 # init -1
        age[isc] = 0
        snowage.append(age)
        snowagetimes.append(times[0])
    else:
        # create age holder, 
        age = new_array(data) - 1.0 # init -1

        # booleans...
        isc = is_snow_covered(data, i)
        new = is_new_snow(data, i)

        # age up snow from previous step,
        dtHours = (times[i] - times[i-1]).total_seconds()/3600.0
        age[isc] = snowage[i-1][isc] + dtHours

        # new snow fall, reset age to 0
        age[new] = 0.0
        
        # no snow cover, set age to -1
        age[~isc] = -1.0

        # append data,
        snowage.append(age)
        snowagetimes.append(times[i])



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
        snowfall.append( new_array(data) ) # zeroed first step
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


# calculate boolean if new snowfall in this step,
def is_new_snow(data, i):
    return data['snowfall']['values'][i] > SNOW_FALL_LIMIT

# calculate boolean if ground snow covered,
def is_snow_covered(data, i):
    return data['snowground']['values'][i] > SNOW_COVER_LIMIT

# calculate boolean for top snow is melting
def is_melting_temp(data, i):
    return data['temp']['values'][i] > 0.0

# get new empty data array to work with,
def new_array(data):
    return data['temp']['values'][0]*0.0

# data set length,
def nsteps(data):
    return len(data['temp']['times'])

def get_times(data):
    return data['temp']['times']