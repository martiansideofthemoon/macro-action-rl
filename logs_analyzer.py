import os
from collections import namedtuple
import matplotlib.pyplot as plt
import re
import math

Stat = namedtuple('Stat', ['d', 'o', 'g'])
def parse_log(fname):
    stats = []
    with open(fname, 'r') as fl:
        def_captured, oob, goals = 0, 0, 0
        for line in fl.readlines():
            line = line.strip()
            if not line.startswith("EndOfTrial"):
                continue
            
            if line.find("CAPTURED_BY_DEFENSE")>=0:
                def_captured += 1
            elif line.find("OUT_OF_BOUNDS")>=0:
                oob += 1
            elif line.find("GOAL"):
                goals += 1

            stats += [Stat(d=def_captured, o=oob, g=goals)]
    return stats

LOGS_DIR = os.path.expanduser("~/sandbox/RL logs")

# job_name->trajectory of stats
# get rid of .log
all_stats = {fn[:-4]: parse_log("%s/%s" % (LOGS_DIR, fn)) for fn in os.listdir(LOGS_DIR) if fn.endswith('.log')}

stat_means, stat_vars = {}, {}
num_stats = {}
for r in all_stats.keys():
    jn = re.sub(r'_seed_[0-9]+', '', r)
    if jn not in stat_means:
        stat_means[jn] = all_stats[r]
        num_stats[jn] = 1.
    else:
        num_stats[jn] += 1.
        _o, _c = stat_means[jn], all_stats[r]
        stat_means[jn] = [Stat(_o[i].d+_c[i].d, _o[i].o+_c[i].o, _o[i].g+_c[i].g) for i in range(min(len(_o), len(_c)))]

for r in all_stats.keys():
    jn = re.sub(r'_seed_[0-9]+', '', r)
    _c = all_stats[r]
    _sm = stat_means[jn]
    if jn not in stat_vars:
        stat_vars[jn] = [Stat((_c[i].d-_sm[i].d)**2, (_c[i].o-_sm[i].o)**2, (_c[i].g-_sm[i].g)**2) for i in range(len(_sm))]
    else:
        _o = stat_vars[jn]
        stat_vars[jn] = [Stat((_c[i].d-_sm[i].d)**2 + _o[i].d, (_c[i].o-_sm[i].o)**2 + _o[i].o, (_c[i].g-_sm[i].g)**2 + _o[i].g) for i in range(len(_sm))]

algs = set([r[:r.find("_lmbda")] for r in stat_means.keys()])
import sys
for alg in algs:
    km = [r for r in stat_means.keys() if r.startswith(alg)]
    parameters = km[0].split('_')
    # print header
    print ("Algorithm: %s" % alg)
    _st = parameters.index('lmbda')
    print ('|' + '|'.join([parameters[i] for i in range(_st, len(parameters), 2)] + ['Number of Episodes', 'Cumm. Regret + sd', 'Cumm. Reward + sd']) + '|')
    for k in km:
        parameters = k.split('_')
        if (len(stat_means[k]) < 1):
            # sys.stderr.write ("ignoring %s\n" %k)
            continue
        print ("|" + "|".join([parameters[i] for i in range(_st+1, len(parameters), 2)] + [str(len(stat_means[k])),
                                                                                           '%f + %f (%d)' % (stat_means[k][-1].g/num_stats[k], math.sqrt(stat_vars[k][-1].g/num_stats[k]), num_stats[k]),
                                                                                           '%f + %f (%d)' % ((stat_means[k][-1].o + stat_means[k][-1].d)/num_stats[k], math.sqrt((stat_vars[k][-1].o + stat_vars[k][-1].d)/num_stats[k]), num_stats[k]) + "|"
        ]))
        
    
    
    
