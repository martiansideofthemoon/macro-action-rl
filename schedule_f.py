import subprocess
import time

BASE_BASH = "macro-action-rl/script.sh"
PORT_INCREMENT = 50
BASE_PORT = 6000
NUM_TRIALS = 150000
SEED = 1

lambda_values = [0, 0.5, 0.8, 0.9, 0.95]
interval_values = [1, 2, 3, 5, 9, 11, 31, 51, 81, 151]

# should be one of: [conditional_figar_sarsa, di_sarsa, reg_sarsa, action_space_sarsa, figar_sarsa]
alg = 'di_sarsa'

with open(BASE_BASH, 'r') as f:
    base_script = f.read()

port_no = BASE_PORT
counter = 0
START_FROM = 0
PARALLEL = 12
run_params = {
    'conditional_figar_sarsa': [''],
    'di_sarsa': ["--step %d" % iv for iv in interval_values],
    'reg_sarsa': ['--regReward %f' % _r for _r in [1E-4, 0.001, 0.01, 0.1, 0.5]],
    'action_space_sarsa': [''],
    'figar_sarsa': ['']
    }
for alg in ['figar_sarsa']:
    for lmbda in lambda_values:
        for run_param in run_params[alg]:
            counter += 1
            if counter <= START_FROM:
                continue
            if counter % PARALLEL == 0:
                time.sleep(3700*4)
                
            job_name = "%s_lmbda_%.2f_step_%s_seed_%d" % (alg, lmbda, run_param.replace(' ', '_'), SEED)
            script = base_script.format(
                job_name,
                port_no,
                alg,
                '--lambda %s %s' % (lmbda, run_param),
                NUM_TRIALS,
                SEED
                )
            port_no += 50
            with open('macro-action-rl/scripts/%s.sh' % job_name, 'w') as f:
                f.write(script)
            command = "sbatch " + 'macro-action-rl/scripts/%s.sh' % job_name
            print(subprocess.check_output(command, shell=True))
