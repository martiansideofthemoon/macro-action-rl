#!/bin/bash

stdbuf -oL ./HFO/bin/HFO --offense-npcs 2 --defense-npcs 1 --defense-agents 1 \
--port 7020 --no-logging --headless --trials 50000 --seed 1 > logs/action_space_sarsa.log 2>&1 &

PID=$!
cd action_space_sarsa
sleep 5

./action_space_sarsa --numAgents 1 --numOpponents 2 --numEpisodes 50000 --basePort 7020 \
--weightId action_space_sarsa_lambda_0.95_seed_1 --lambda 0.95

kill -SIGINT $PID
sleep 5
cd ..
