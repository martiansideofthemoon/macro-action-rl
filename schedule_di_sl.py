import argparse
import pxssh
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument("-sl", "--sl", default=2, type=int, help="Which software lab")
parser.add_argument("-start", "--start", default=0, type=int, help="Which PC to start from")
parser.add_argument("-user", "--user", default='user', type=str, help="Username")
parser.add_argument("-password", "--password", default='pass', type=str, help="Password")

args = parser.parse_args()

lambda_values = [0, 0.5, 0.8, 0.9, 0.95]
interval_values = [1, 2, 4, 8, 16, 32]
seeds = [2, 5]
NUM_TRIALS = 50000

port_no = 6050

with open('script-sl.sh', 'r') as f:
    base_script = f.read()

counter = args.start

for seed in seeds:
    for lmbda in lambda_values:
        for interval in interval_values:
            job_name = "di_sarsa_lmbda_%.2f_step_%d_seed_%d" % (lmbda, interval, seed)
            script = base_script.format(
                job_name,
                port_no,
                'di_sarsa',
                '--lambda %s --step %s' % (lmbda, interval),
                NUM_TRIALS,
                seed
            )
            with open('scripts/%s.sh' % job_name, 'w') as f:
                f.write(script)
            s = pxssh.pxssh()
            counter += 1
            while True:
                try:
                    s.login('sl%d-%d.cse.iitb.ac.in' % (args.sl, counter), args.user, args.password)
                    break
                except:
                    print "SSH session failed on login."
                    counter += 1
                    s = pxssh.pxssh()
            print "SSH session login successful on sl%d-%d.cse.iitb.ac.in" % (args.sl, counter)
            commands = [
                'killall screen',
                'killall -9 rcssserver',
                'chmod 777 %s.sh' % job_name,
                'screen -S %s -d -m ./%s.sh' % (job_name, job_name)
            ]
            for command in commands:
                print command
                s.sendline(command)
                s.prompt()         # match the prompt
            s.logout()

# command = "scp scripts/* %s@sl%d-1.cse.iitb.ac.in:~/" % (args.user, args.sl)
# print(subprocess.check_output(command, shell=True))
