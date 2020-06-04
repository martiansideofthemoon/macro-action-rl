#!/bin/bash
#
#SBATCH --job-name=hfo_repetition_{0}
#SBATCH -o swarm-outputs3/hfo_repetition_{0}.txt  # output file
#SBATCH --time=11:59:00
#SBATCH --partition=defq
#SBATCH --cpus-per-task=3
#SBATCH --mem=7000
#SBATCH -d singleton
#SBATCH --ntasks-per-node=1

cd /mnt/nfs/work1/miyyer/kalpesh/projects/macro-action-rl

stdbuf -oL ./HFO/bin/HFO --offense-npcs 2 --defense-npcs 1 --defense-agents 1 \
--port {1} --no-logging --headless --deterministic --trials 52000 --seed {4} > logs3/server_{0}.log 2>&1 &

PID=$!
cd {2}
sleep 5

./{2} --numAgents 1 --numOpponents 2 --numEpisodes 50000 --numEpisodesTest 2000 --basePort {1} \
--weightId {0} {3}

kill -SIGINT $PID
sleep 5
cd ..
