#!/bin/bash

stdbuf -oL ./HFO/bin/HFO --offense-npcs 3 --defense-npcs 1 --defense-agents 2 \
--port 7085 --no-logging --headless --trials 50000 --seed 1 > logs/conditional_figar_sarsa.log 2>&1 &

PID=$!
cd conditional_figar_sarsa
sleep 5

./conditional_figar_sarsa --numAgents 2 --numOpponents 3 --numEpisodes 50000 --basePort 7085 \
--weightId conditional_figar_sarsa_lambda_0.5_seed_1 --lambda 0.5

kill -SIGINT $PID
sleep 5
cd ..
