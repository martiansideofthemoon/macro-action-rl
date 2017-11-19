#!/bin/bash

#SBATCH -p speech-cpu
#SBATCH -c4
#SBATCH -o macro-action-rl/logs/client_{0}.log

cd macro-action-rl
stdbuf -oL ./HFO/bin/HFO --offense-npcs 2 --defense-npcs 1 --defense-agents 1 --port {1} --no-logging --headless --trials {4} --seed {5} > /users/extusr/varunb/macro-action-rl-logs/server_{0}.log 2>&1 &
PID=$!
cd {2}
sleep 5
./{2} --numAgents 1 --numOpponents 2 --numEpisodes {4} --basePort {1} --weightId {0} {3}
kill -SIGINT $PID
sleep 5
cd ..
