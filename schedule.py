import subprocess
import time

BASE_BASH = "script.sh"
PORT_INCREMENT = 10
BASE_PORT = 9000
NUM_TRIALS = 50000
seeds = [2,3]

lambda_values = [0, 0.5, 0.8, 0.9, 0.95]
interval_values = [1, 2, 3, 5, 9, 11, 31, 51, 81, 151]

# should be one of: [conditional_figar_sarsa, di_sarsa, reg_sarsa, action_space_sarsa, figar_sarsa]
alg = 'di_sarsa'

with open(BASE_BASH, 'r') as f:
    base_script = f.read()

port_no = BASE_PORT
counter = 0
run_params = {
    'conditional_figar_sarsa': [''],
    'di_sarsa': ["--step %d" % iv for iv in interval_values],
    'reg_sarsa': ['--regReward %f' % _r for _r in [1E-4, 0.001, 0.01, 0.1, 0.5]],
    'action_space_sarsa': [''],
    'figar_sarsa': ['']
    }
run_params = {"di_sarsa": ["--step 1 --lambda %.2f" % lmbda for lmbda in lambda_values]}

for alg in run_params.keys():
    for SEED in seeds:
        for run_param in run_params[alg]:
            counter += 1
                
            job_name = "%s_%s_seed_%d" % (alg, run_param.replace(' ', '_').replace('--', ''), SEED)
            script = base_script.format(
                job_name,
                port_no,
                alg,
                '%s' % (run_param),
                NUM_TRIALS,
                SEED
            )
            port_no += 50
            with open('scripts/%s.sh' % job_name, 'w') as f:
                f.write(script)

import os
os.system("chmod a+x scripts/*")
