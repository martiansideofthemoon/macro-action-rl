#!/bin/bash

stdbuf -oL ./HFO/bin/HFO --offense-npcs 2 --defense-npcs 1 --defense-agents 1 --port 7160 --no-logging --headless --trials 50000 --seed 1 > logs/server_di_sarsa_lambda_0.500000_step_64_seed_1.log 2>&1 &
PID=$!
cd di_sarsa
sleep 5
./di_sarsa --numAgents 1 --numOpponents 2 --numEpisodes 50000 --basePort 7160 --weightId di_sarsa_lambda_0.500000_step_64_seed_1 --lambda 0.500000 --step 32
kill -SIGINT $PID
sleep 5
cd ..
