import os
from collections import namedtuple
import matplotlib.pyplot as plt
import re
import math
import sys
import numpy as np
from multiprocessing import Pool

Stat = namedtuple('Stat', ['d', 'o', 'g'])
def parse_log(fname):
    stats = []
    with open(fname, 'r') as fl:
        def_captured, oob, goals = 0, 0, 0
        l = 0
        test_start = False
        for line in fl.readlines():
            line = line.strip()
            l += 1
            if not line.startswith("EndOfTrial"):
                continue

            # if line.find(" / 50000 ") >= 0:
            #     test_start = True
            #     continue
            # if not test_start:
            #     continue
            
            if line.find("CAPTURED_BY_DEFENSE")>=0 or line.find("OUT_OF_TIME")>=0:
                def_captured += 1.
            elif line.find("OUT_OF_BOUNDS")>=0:
                oob += 1.
            elif line.find("GOAL"):
                goals += 1.

            stats += [Stat(d=def_captured, o=oob, g=goals)]
    if len(stats)>1900:
        return stats
    else: return []

#LOGS_DIR = os.path.expanduser("~/Downloads/RL Logs 2/")
LOGS_DIR = "logs"

# job_name->trajectory of stats
# get rid of .log
fns = [fn for fn in os.listdir(LOGS_DIR) if fn.endswith('.log')]
fni = 0
all_stats = {}
for fn in fns:
    fni += 1
    _ = parse_log("%s/%s" % (LOGS_DIR, fn))
    if len(_)<1:
        continue
    all_stats[fn[:-4]] = _
    sys.stdout.write("\rRead: %d/%d logs" % (fni, len(fns)))
    sys.stdout.flush()
sys.stdout.write("\n")

for jn in all_stats.keys():
    print ("%s %d" % (jn, len(all_stats[jn])))

stat_means, stat_vars = {}, {}
rewards_per_config = {}
num_stats = {}
for r in all_stats.keys():
    jn = re.sub(r'_seed_[0-9]+', '', r)
    stat = all_stats[r][-1]
    # rewd = (sum(_ds) + sum(_os))/sum(_gs)
    rewd = (stat.d + stat.o)/(stat.g + stat.d + stat.o)
    rewards_per_config[jn] = rewards_per_config.get(jn, []) + [rewd]
    
    if jn not in stat_means:
        stat_means[jn] = all_stats[r]
        num_stats[jn] = 1.
    else:
        num_stats[jn] += 1.
        _o, _c = stat_means[jn], all_stats[r]
        stat_means[jn] = [Stat(_o[i].d+_c[i].d, _o[i].o+_c[i].o, _o[i].g+_c[i].g) for i in range(min(len(_o), len(_c)))]

for k in rewards_per_config.keys():
    rewards_per_config[k] = np.array(rewards_per_config[k])
        
for jn in stat_means.keys():
    _sm = stat_means[jn]
    _n = num_stats[jn]
    stat_means[jn] = [Stat(d=_sm[i].d/_n, o=_sm[i].o/_n, g=_sm[i].g/_n) for i in range(len(_sm))]
for r in all_stats.keys():
    jn = re.sub(r'_seed_[0-9]+', '', r)
    _c = all_stats[r]
    if jn not in stat_means:
        continue
    _sm = stat_means[jn]
    if jn not in stat_vars:
        stat_vars[jn] = [Stat((_c[i].d-_sm[i].d)**2, (_c[i].o-_sm[i].o)**2, (_c[i].g-_sm[i].g)**2) for i in range(len(_sm))]
    else:
        _o = stat_vars[jn]
        stat_vars[jn] = [Stat((_c[i].d-_sm[i].d)**2 + _o[i].d, (_c[i].o-_sm[i].o)**2 + _o[i].o, (_c[i].g-_sm[i].g)**2 + _o[i].g) for i in range(len(_sm))]

for jn in stat_vars.keys():
    _sm = stat_vars[jn]
    _n = num_stats[jn]
    stat_vars[jn] = [Stat(d=_sm[i].d/_n, o=_sm[i].o/_n, g=_sm[i].g/_n) for i in range(len(_sm))]
        
algs = set([r[:r.find("_step")] for r in stat_means.keys()])
import sys
el = min([len(_s) for _s in stat_means.values() if len(_s)>0]) - 1
for alg in algs:
    km = [r for r in sorted(stat_means.keys(), key=lambda x: int(x.split('_')[2])) if r.startswith(alg)]
    parameters = km[0].split('_')
    # print header
    print ("Algorithm: %s" % alg)
    _st = parameters.index('step')
    print ('|' + '|'.join([parameters[i] for i in range(_st, len(parameters), 2)] + ['Number of Episodes', 'Cumm. Regret + sd', 'Cumm. Reward + sd', '%captured', '%goal']) + '|')
    for k in km:
        parameters = k.split('_')
        if (len(stat_means[k]) < 1):
            # sys.stderr.write ("ignoring %s\n" %k)
            continue
        rewd = stat_means[k][el].o + stat_means[k][el].d
        _g = stat_means[k][el].g
        print ("|" + "|".join([parameters[i] for i in range(_st+1, len(parameters), 2)] + [str(el+1),
                                                                                           '%.3f + %.3f (%d)' % (stat_means[k][el].g, math.sqrt(stat_vars[k][el].g), num_stats[k]),
                                                                                           '%.3f (%d)' % (rewd, num_stats[k]),
                                                                                           '%.3f (%.3f)' % (np.mean(rewards_per_config[k]), np.std(rewards_per_config[k]) / np.sqrt(len(rewards_per_config[k]))), ('%.3f' % (_g/(el+1)))+'|'
        ]))
        
    
    
    
