import subprocess
import time

BASE_BASH = "macro-action-rl/script.sh"
PORT_INCREMENT = 50
BASE_PORT = 6000
NUM_TRIALS = 150000
SEED = 1

lambda_values = [0, 0.25, 0.5, 0.75, 0.85, 0.9, 0.95]
interval_values = [1, 2, 4, 8, 16, 32]

with open(BASE_BASH, 'r') as f:
    base_script = f.read()

port_no = BASE_PORT
counter = 0
START_FROM = 0
PARALLEL = 12
for lmbda in lambda_values:
    for interval in interval_values:
        counter += 1
        if counter <= START_FROM:
            continue
        if counter % PARALLEL == 0:
            time.sleep(3700*4)
        job_name = "di_sarsa_lmbda_%.2f_step_%d_seed_%d" % (lmbda, interval, SEED)
        script = base_script.format(
            job_name,
            port_no,
            'di_sarsa',
            '--lambda %s --step %s' % (lmbda, interval),
            NUM_TRIALS,
            SEED
        )
        port_no += 50
        with open('macro-action-rl/scripts/%s.sh' % job_name, 'w') as f:
            f.write(script)
        command = "sbatch " + 'macro-action-rl/scripts/%s.sh' % job_name
        print(subprocess.check_output(command, shell=True))
