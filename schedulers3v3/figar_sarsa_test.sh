#!/bin/bash

stdbuf -oL ./HFO/bin/HFO --offense-npcs 3 --defense-npcs 1 --defense-agents 2 \
--port 7225 --no-logging --headless --deterministic --trials 2000 --seed 1 > logs/figar_sarsa.log 2>&1 &

PID=$!
cd figar_sarsa
sleep 5

./figar_sarsa --numAgents 2 --numOpponents 3 --numEpisodes 0 --numEpisodesTest 2000 --basePort 7225 \
--weightId figar_sarsa_lambda_0.0_seed_1_episode_50000 --load --lambda 0.0 > /dev/null

kill -SIGINT $PID
sleep 5
cd ..
