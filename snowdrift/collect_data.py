import pygrib
import logging
import numpy as np
from datetime import datetime, timedelta

# output paremeter defs...
TYPE_OF_LEVEL=105
LEVEL=0
SNOW_COVER_AGE_PARAMETER=145
DRIFT_ACCUMULATION_PARAMETER=146
MOBILITY_INDEX_PARAMETER=147
SNOW_DRIFT_VALUE_PARAMETER=148

# default data collection config...
config = {
    'snow_ac': 'heightAboveGround:0:184',
    'snow': 'heightAboveGround:0:64',
    'surface-temp': 'heightAboveGround:0:11',
    'wind-u': 'heightAboveGround:10:33',
    'wind-v': 'heightAboveGround:10:34',
}

def collectData(files, config=config):
    # reverse mapping of config dict for convenience,
    id2Par = {v: k for k, v in config.items()}

    # create data holder,
    data = {}

    for f in files:
        # open the files...
        try:
            G = pygrib.open(f)
        except OSError as e:
            logging.error("failed to open file %r"%f)
            raise e

        logging.info("collecting from %r"%f)

        # scan for data
        for g in G:
            # read the msg identifiers
            toLevel = g['typeOfLevel']
            level = g['level']
            ioPar = g['indicatorOfParameter']
            # construct string unique identity
            id = "%s:%d:%d"%(toLevel, level, ioPar)

            # check against config,
            if id in id2Par:
                # collect this data,
                par = id2Par[id]
                if par not in data:
                    logging.info(" - found %r"%par)
                    data[par] = {'times': [], 'values':[]}
                # pick out data...
                vals = g.values.astype(np.float32)

                # convert any masked array data...
                if hasattr(vals, 'mask'):
                    vals = np.ma.getdata(vals)

                # calculate step valid time...
                t = g.validDate
                ## WARNING: the valid time of step,
                ##    can be differently implemented in some forecasts,
                ##    this works with ecmwf, Harmonie and IGB data...
                ##    TODO: It may be necessary to add some logic here
                ##          for other fc model outputs like NCEP models
                t += timedelta(hours = g.step * g.stepUnits)
                
                # append data
                times = data[par]['times']
                values = data[par]['values']
                times.append(t)
                values.append(vals)
        # close file
        G.close()

    # Sorting and consistency checks here...

    # sort time steps,
    # data should be returned in correct order
    logging.info('time sorting loaded parameters')

    # load data summary
    summary(data)

    # Consistency checks, e.g. no. steps and time stamps
    logging.info('preforming final consistency checks')
    # check that all params and times are equivalent...
    allTimes = [data[x]['times'] for x in data]
    allN = [len(ts) for ts in allTimes]
    # must all be same length...
    logging.info("checking loaded params length are consistent")
    for i in range(1, len(allN)):
        prev = allN[i-1]
        curr = allN[i]
        if prev != curr:
            logging.error(" - FAIL")
            raise IOError("inconsistent number of parameter steps found")
    logging.info(" - OK")
    # check all time steps are equivalent,
    logging.info("checking time steps across all loaded params")
    for i in range(1, len(allTimes)):
        for k in range(len(allTimes[0])):
            if allTimes[i][k] != allTimes[i-1][k]:
                logging.error(" - FAIL")
                raise IOError("time steps dont match across all input data")
    logging.info(" - OK")


def summary(data):
    print("Data summary:")
    for k in data:
        print("  %s:"%k)
        times = data[k]['times']
        values = data[k]['values']
        print("    steps: %d"%len(times))
        print("    start/stop: %s/%s"%(times[0],times[-1]))



