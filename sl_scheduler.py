import argparse
from pexpect import pxssh
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument("-sl", "--sl", default=2, type=int, help="Which software lab")
parser.add_argument("-user", "--user", default='user', type=str, help="Username")
parser.add_argument("-password", "--password", default='pass', type=str, help="Password")
parser.add_argument("-p", "--prefix", dest='p', default='', type=str, help="The prefix of the scripts to run. For ex: reg_sarsa")
parser.add_argument("-f", dest="f", default=None, type=str,
                    help="""A file containing list of jobs to be run. 
                    For ex: 
                    server_conditional_figar_sarsa_lambda_0.800000_seed_1.sh
                    server_reg_sarsa_lambda_0.950000_regReward_2.000000_seed_2.sh
                    ...
                    """)

args = parser.parse_args()

import os
_s = '~/repos/macro-action-rl'
SCRIPTS_FLDR = os.path.expanduser('~/repos/macro-action-rl/scripts')
if args.f is None:
    sh_scripts = [f for f in os.listdir(SCRIPTS_FLDR) if f.startswith(args.p)]
else:
    sh_scripts = []
    print (args.f)
    with open(args.f, 'r') as rf:
        for line in rf.readlines():
            _l = line.strip()
            if os.path.exists("scripts/%s" % _l):
                sh_scripts.append(_l)
            else:
                print ("%s not found in scripts folder" % _l)
        
print ("Found %d scripts matching the prefix: %s in the scripts folder" % (len(sh_scripts), args.p))

counter = 0
for sh_script in sh_scripts:
    job_name = sh_script[:-3]
    s = pxssh.pxssh()
    counter += 1
    while True:
        try:
            s.login('sl%d-%d.cse.iitb.ac.in' % (args.sl, counter), args.user, args.password)
            break
        except:
            print ("SSH session failed on login.")
            counter += 1
            s = pxssh.pxssh()
    print ("SSH session login successful on sl%d-%d.cse.iitb.ac.in" % (args.sl, counter))
    commands = [
        'killall screen',
        'killall -9 rcssserver && sleep 2',
        'cd %s' % _s,
        'chmod 777 scripts/%s.sh' % job_name,
        'screen -S %s -d -m scripts/%s.sh' % (job_name, job_name)
    ]
    for command in commands:
        print (command)
        s.sendline(command)
        s.prompt()         # match the prompt
    s.logout()

# command = "scp scripts/* %s@sl%d-1.cse.iitb.ac.in:~/" % (args.user, args.sl)
# print(subprocess.check_output(command, shell=True))
