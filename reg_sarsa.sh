#!/bin/bash

stdbuf -oL ./HFO/bin/HFO --offense-npcs 2 --defense-npcs 1 --defense-agents 1 \
--port 7135 --no-logging --headless --trials 50000 --seed 1 > logs/reg_sarsa.log 2>&1 &

PID=$!
cd reg_sarsa
sleep 5

./reg_sarsa --numAgents 1 --numOpponents 2 --numEpisodes 50000 --basePort 7135 \
--weightId reg_sarsa_lambda_0.95_regReward_2.0_seed_1 --lambda 0.95 --regReward 2.0

kill -SIGINT $PID
sleep 5
cd ..
