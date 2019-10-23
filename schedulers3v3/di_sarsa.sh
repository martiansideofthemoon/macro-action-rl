#!/bin/bash

stdbuf -oL ./HFO/bin/HFO --offense-npcs 3 --defense-npcs 1 --defense-agents 2 \
--port 7160 --no-logging --headless --deterministic --trials 52000 --seed 1 > logs/di_sarsa.log 2>&1 &

PID=$!
cd di_sarsa
sleep 5

./di_sarsa --numAgents 2 --numOpponents 3 --numEpisodes 50000 --numEpisodesTest 2000 --basePort 7160 \
--weightId di_sarsa_lambda_0.5_step_32_seed_1 --lambda 0.5 --step 32 > ../logs/di_sarsa_debug.log

kill -SIGINT $PID
sleep 5
cd ..
