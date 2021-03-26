import pygrib
import logging
import numpy as np
from datetime import datetime, timedelta
from more_itertools import sort_together

# default data collection config...
config = {
    'snowac': {
        'id': 'heightAboveGround:0:184',
        # override unit if not provided...
        'unit': 'kg m**-2'
    },
    # Snow on ground, keeps track of snow covered
    # and snow free areas.
    'snowground': {
        'id': 'heightAboveGround:0:65'
    },
    # temp should ideally be surface temperature
    # if model has it
    'temp': {
        'id': 'heightAboveGround:0:11',
        #'id': 'heightAboveGround:2:11'
    },
    'wind-u': {
        'id': 'heightAboveGround:10:33'
    },
    'wind-v': {
        'id': 'heightAboveGround:10:34'
    }
}

def collectData(files, config=config):
    # reverse mapping of config dict for convenience,
    id2Par = {v['id']: k for k, v in config.items()}

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
            unit = g['units']
            # construct string unique identity
            id = "%s:%d:%d"%(toLevel, level, ioPar)

            # check against config,
            if id in id2Par:
                # collect this data,
                par = id2Par[id]
                if par not in data:
                    logging.info(" - found %r"%par)
                    # check if input config overrides unit
                    if config[par].get('unit'):
                        unit = config[par].get('unit')
                        logging.info("   - overriding unit as %r"%unit)
                    # create data entry for this par...
                    data[par] = {'times': [], 'values':[], 'unit': unit}

                # pick out data...
                vals = g.values.astype(np.float32)

                # convert any masked array data...
                if hasattr(vals, 'mask'):
                    vals = np.ma.getdata(vals)

                # convert units if necessary,
                if unit == 'K':
                    vals -= 273.15
                    data[par]['unit'] = u'°C'

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
    for par in data:
        times = data[par]['times']
        values = data[par]['values']
        res = sort_together((times, values))
        data[par]['times'] = res[0]
        data[par]['values'] = res[1]

    # load data summary
    summary(data)

    # consistency checks on input data,
    check_consistency(data)

    return data

# collect a single appropriate msg from grib forecast,
# for later use as template in writing snow drift results 
def get_template_msg(file):
    # reverse mapping of config dict for convenience,
    id2Par = {v['id']: k for k, v in config.items()}

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
        unit = g['units']
        # construct string unique identity
        id = "%s:%d:%d"%(toLevel, level, ioPar)

        # check against config,
        if id in id2Par:
            # collect this data,
            pass

    # if here failed to find template msg
    G.close()
    raise IOError("could not find a template msg in %r"%file)

def check_consistency(data):
    # Consistency checks, e.g. no. steps and time stamps
    logging.info('preforming data consistency checks')
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
    print("-----------------------------------")
    print("data summary:")
    print("-----------------------------------")
    mm = minmax(data)
    for k in data:
        print("  %s:"%k)
        times = data[k]['times']
        n = len(times)
        values = data[k]['values']
        unit = data[k]['unit']
        mi = mm[k]['min']
        ma = mm[k]['max']
        if n == 0:
            print("    NO DATA")
        else:
            print("    steps:       %d"%n)
            print("    min/max:     %.1f/%.1f %s"%(mi,ma,unit))
            print("    start/stop:  %s/%s"%(times[0],times[-1]))
    print("-----------------------------------")

def minmax(data):
    mm = {}
    for k in data:
        vs = data[k]['values']
        # if empty...
        if len(vs) == 0:
            mm[k] = {'min': np.nan, 'max': np.nan}
        if k not in mm:
            mm[k] = {'min': vs[0].min(), 'max': vs[0].max()}
        mi = mm[k]['min']
        ma = mm[k]['max']
        for v in vs:
            tma = v.max()
            tmi = v.min()
            if tma > ma:
                mm[k]['max'] = tma
            if tmi < mi:
                mm[k]['min'] = tmi
    return mm




