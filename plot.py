import os
import numpy as np
import cPickle
from collections import namedtuple
import matplotlib.pyplot as plt
import re
import math
import sys

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties

pp = PdfPages('expt1.pdf')
plt.figure()
plt.clf()

Stat = namedtuple('Stat', ['d', 'o', 'g'])


def parse_log(fname):
    stats = []
    with open(fname, 'r') as fl:
        def_captured, goals = 0, 0
        episodes = 0
        l = 0
        for line in fl.readlines():
            line = line.strip()
            l += 1
            if not line.startswith("EndOfTrial"):
                continue
            episodes += 1
            if line.find("CAPTURED_BY_DEFENSE") >= 0 or line.find("OUT_OF_TIME") >= 0 or line.find("OUT_OF_BOUNDS") >= 0:
                def_captured += 1.
            elif line.find("GOAL"):
                goals += 1.

            stats += [goals / episodes]
    if len(stats) > 40000:
        return stats
    else:
        return []

LOGS_DIR = "sl2-logs"
logfile = re.compile(r'server_(.*)_sarsa_(lambda|lmbda)_(\d*\.?\d*)_((step|regReward)_(\d*\.?\d*)_)?seed_(.*)\.log')

# job_name->trajectory of stats
# get rid of .log
fns = [fn for fn in os.listdir(LOGS_DIR) if fn.endswith('.log')]
runs = {
    'di': [],
    'figar': [],
    'reg': [],
    'conditional_figar': [],
    'action_space': []
}
fni = 0
all_stats = {}
for fn in fns:
    matches = re.search(logfile, fn)
    runs[matches.group(1)].append({
        'lambda': float(matches.group(3)),
        'extra': matches.group(5),
        'extra_value': matches.group(6) if matches.group(6) is None else float(matches.group(6)),
        'seed': int(matches.group(7)),
        'file': fn
    })
    fni += 1
    sys.stdout.write("\rRead: %d/%d logs" % (fni, len(fns)))
    sys.stdout.flush()
sys.stdout.write("\n")

plot_logs = [
    ('di', ('lambda', 0.5), ('step', 32)),
    ('figar', ('lambda', 0)),
    ('reg', ('lambda', 0.95), ('regReward', 2)),
    ('action_space', ('lambda', 0.95)),
    ('conditional_figar', ('lambda', 0.5))
]

# plot_logs = [
#     ('di', ('lambda', 0), ('step', 32)),
#     ('di', ('lambda', 0.5), ('step', 32)),
#     ('di', ('lambda', 0.8), ('step', 32)),
#     ('di', ('lambda', 0.9), ('step', 32)),
#     ('di', ('lambda', 0.95), ('step', 32)),
# ]

for p in plot_logs:
    algo = p[0]
    params = p[1:]
    files = []
    for run in runs[algo]:
        match = True
        for key, value in params:
            if key in run and run[key] != value:
                match = False
            elif run['extra'] == key and run['extra_value'] != value:
                match = False
        if match:
            files.append(run['file'])
    all_stats = []
    for fn in files:
        _ = parse_log("%s/%s" % (LOGS_DIR, fn))
        if len(_) < 1:
            continue
        all_stats.append(_)
    episodes = min([len(a) for a in all_stats])
    all_stats = np.array([a[:episodes] for a in all_stats])
    mean_stats = np.mean(all_stats, axis=0)
    episode_num = np.arange(len(mean_stats))
    std_stats = np.std(all_stats, axis=0)

    str_params = ', '.join(['%s: %s' % (k, str(v)) for k, v in params])
    plt.plot(episode_num[100:], mean_stats[100:], label="%s - %s" % (algo, str_params))

legend = plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=3)

plt.xlabel('episodes')
plt.ylabel('percent goals scored')
pp.savefig()
pp.close()
plt.show()
