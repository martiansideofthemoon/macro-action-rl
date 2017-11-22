import subprocess
import time

BASE_BASH = "script.sh"
PORT_INCREMENT = 5
BASE_PORT = 7000
NUM_TRIALS = 50000
seeds = [1, 2, 3]

lambda_values = [0, 0.8, 0.9, 0.95]
interval_values = [1, 2, 3, 5, 9, 11, 31, 51, 81, 151]

# should be one of: [conditional_figar_sarsa, di_sarsa, reg_sarsa, action_space_sarsa, figar_sarsa]
alg = 'di_sarsa'

with open(BASE_BASH, 'r') as f:
    base_script = f.read()

port_no = BASE_PORT
counter = 20
#reg_vals = [1E-4, 0.001, 0.01, 0.1, 0.5]
reg_vals = [1, 2, 3, 4]
run_params = {
    'conditional_figar_sarsa': ['--lambda %f' % _l for _l in lambda_values],
    #'di_sarsa': ["--step %d" % iv for iv in interval_values],
    'reg_sarsa': ['--lambda %f --regReward %f' % (_l, _r) for _r in reg_vals for _l in lambda_values],
    'action_space_sarsa': ['--lambda %f' % _l for _l in lambda_values],
    'figar_sarsa': ['--lambda %f' % _l for _l in lambda_values]
    }
#run_params = {"di_sarsa": ["--step 1 --lambda %.2f" % lmbda for lmbda in lambda_values]}

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
            port_no += PORT_INCREMENT
            with open('scripts/%s.sh' % job_name, 'w') as f:
                f.write(script)

import os
os.system("chmod a+x scripts/*")
