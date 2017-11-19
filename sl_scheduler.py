import argparse
import pxssh
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument("-sl", "--sl", default=2, type=int, help="Which software lab")
parser.add_argument("-user", "--user", default='user', type=str, help="Username")
parser.add_argument("-password", "--password", default='pass', type=str, help="Password")
parser.add_argument("-p", "--prefix", type=str, help="The prefix of the scripts to run. For ex: reg_sarsa", required=True)

args = parser.parse_args()

import os
SCRIPTS_FLDR = 'scripts'
sh_scripts = [f for f in os.listdir(SCRIPTS_FLDR) if f.startswith(args.p)]
print ("Found %d scripts matching the prefix in the scripts folder" % len(sh_scripts))

for sh_script in sh_scripts:
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
    command = 'screen -S %s -d -m %s' % (job_name, os.path.sep.join([SCRIPTS_FLDR, sh_script]))
    print (command)
    s.sendline(command)
    s.prompt()         # match the prompt
    print (s.before)     # print everything before the prompt.
    s.logout()

# command = "scp scripts/* %s@sl%d-1.cse.iitb.ac.in:~/" % (args.user, args.sl)
# print(subprocess.check_output(command, shell=True))
