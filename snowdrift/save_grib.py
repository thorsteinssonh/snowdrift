import pygrib
import logging

TYPE_OF_LEVEL=105
LEVEL=0
SNOWAGE_PARAMETER=145
DRIFTACCUMULATION_PARAMETER=146
MOBILITY_PARAMETER=147
DRIFT_PARAMETER=148

# Saves snowdrift parameters to a new grib file,
# appending each message.
# Requires a template message from source forecast
# in oreder to replace values and write in compatible
# GRIB formatting to the source.
def save_grib(data, filename, template_msg):
    msg = template_msg

    # create file,
    out = open(filename,'wb')

    # get handle on snowdrift parameter data
    times = data['temp']['times']
    n = len(times)
    drift = data['drift']['values']
    snowage = data['snowage']['values']
    driftacc = data['driftacc']['values']
    mobility = data['mobility']['values']

    #for k in msg.keys():
    #    print(k, msg[k])

    # loop through snowdrift results,
    # and write GRIB msgs...
    for i in range(n):
        # drift
        logging.info("writing drift step %d"%i)
        msg.level = LEVEL
        msg['indicatorOfParameter'] = DRIFT_PARAMETER       
        # NOTE: Forecast time steps may need improvement
        #       for other forecast sources like NCEP.
        #       Keep an eye on this for later improvements if needed.
        msg['startStep'] = i
        msg['endStep'] = i
        msg['values'] = drift[i]
        out.write(msg.tostring())

        # snowage
        logging.info("writing snowage step %d"%i)
        msg.level = LEVEL
        msg['indicatorOfParameter'] = SNOWAGE_PARAMETER       
        # NOTE: Forecast time steps may need improvement
        #       for other forecast sources like NCEP.
        #       Keep an eye on this for later improvements if needed.
        msg['startStep'] = i
        msg['endStep'] = i
        msg['values'] = snowage[i]
        out.write(msg.tostring())

        # driftacc
        logging.info("writing driftacc step %d"%i)
        msg.level = LEVEL
        msg['indicatorOfParameter'] = DRIFTACCUMULATION_PARAMETER       
        # NOTE: Forecast time steps may need improvement
        #       for other forecast sources like NCEP.
        #       Keep an eye on this for later improvements if needed.
        msg['startStep'] = i
        msg['endStep'] = i
        msg['values'] = driftacc[i]
        out.write(msg.tostring())

        # mobility
        logging.info("writing mobility step %d"%i)
        msg.level = LEVEL
        msg['indicatorOfParameter'] = MOBILITY_PARAMETER       
        # NOTE: Forecast time steps may need improvement
        #       for other forecast sources like NCEP.
        #       Keep an eye on this for later improvements if needed.
        msg['startStep'] = i
        msg['endStep'] = i
        msg['values'] = mobility[i]
        out.write(msg.tostring())


    out.close()