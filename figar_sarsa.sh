#!/bin/bash

stdbuf -oL ./HFO/bin/HFO --offense-npcs 2 --defense-npcs 1 --defense-agents 1 --port 7225 --no-logging --headless --trials 50000 --seed 1 > logs/server_figar_sarsa_lambda_0.000000_seed_1.log 2>&1 &
PID=$!
cd figar_sarsa
sleep 5
./figar_sarsa --numAgents 1 --numOpponents 2 --numEpisodes 50000 --basePort 7225 --weightId figar_sarsa_lambda_0.000000_seed_1 --lambda 0.000000
kill -SIGINT $PID
sleep 5
cd ..
