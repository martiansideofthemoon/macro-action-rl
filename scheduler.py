import argparse
import subprocess
from multiprocessing import Pool

parser = argparse.ArgumentParser()

parser.add_argument("-p", "--prefix", dest='prefix', default="", type=str, help="The prefix of the scripts to run. For ex: reg_sarsa")
parser.add_argument("-s", "--substr", dest='substr', default="", type=str, help="Filter script names that contain this substr. For ex: seed_1.")

args = parser.parse_args()

import os
SCRIPTS_FLDR = os.path.expanduser('~/repos/macro-action-rl/scripts')
job_names = [f for f in os.listdir(SCRIPTS_FLDR) if f.startswith(args.prefix) and f.endswith('.sh') and f.find(args.substr)>=0]

print ("Found %d scripts matching the prefix: %s in the scripts folder" % (len(job_names), args.prefix))

def _r(jn):
    cmd = os.path.sep.join([SCRIPTS_FLDR, jn])
    print (cmd)
    os.system(cmd)

p = Pool(30)
print (p.map(_r, job_names))
