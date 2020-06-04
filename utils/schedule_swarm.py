import subprocess
import time

import os

BASE_BASH = "utils/script_swarm.sh"
PORT_INCREMENT = 5
BASE_PORT = 5000
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

lambda_values = [0.8]
# lambda_values = [0.5]
interval_values = [16]

# should be one of: [conditional_figar_sarsa, di_sarsa, reg_sarsa, action_space_sarsa, figar_sarsa]
alg = 'di_sarsa'

with open(BASE_BASH, 'r') as f:
    base_script = f.read()

port_no = BASE_PORT
counter = 20
reg_vals = [0.5]
# reg_vals = [2]
run_params = {
    'conditional_figar_sarsa': ['--lambda %f' % _l for _l in lambda_values],
    'di_sarsa': ["--step %d --lambda %f" % (iv, _l) for _l in lambda_values for iv in interval_values],
    'reg_sarsa': ['--lambda %f --regReward %f' % (_l, _r) for _r in reg_vals for _l in lambda_values],
    'action_space_sarsa': ['--lambda %f' % _l for _l in lambda_values],
    'figar_sarsa': ['--lambda %f' % _l for _l in lambda_values]
}
# run_params = {"di_sarsa": ["--step 1 --lambda %.2f" % lmbda for lmbda in lambda_values]}

for SEED in seeds:
    for run_param in run_params[alg]:
        counter += 1
        job_name = "%s_%s_seed_%d" % (alg, run_param.replace(' ', '_').replace('--', ''), SEED)
        script = base_script.format(
            job_name,
            port_no,
            alg,
            '%s' % (run_param),
            SEED
        )
        port_no += PORT_INCREMENT
        with open('swarm-schedulers3/%s.sh' % job_name, 'w') as f:
            f.write(script)
        subprocess.check_output('chmod +x swarm-schedulers3/%s.sh' % job_name, shell=True)
        print(subprocess.check_output('sbatch swarm-schedulers3/%s.sh' % job_name, shell=True))
