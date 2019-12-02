#!/bin/bash

stdbuf -oL ./HFO/bin/HFO --offense-npcs 3 --defense-npcs 1 --defense-agents 2 \
--port 7085 --no-logging --headless --deterministic --trials 2000 --seed 1 > logs/conditional_figar_sarsa.log 2>&1 &

PID=$!
cd conditional_figar_sarsa
sleep 5

./conditional_figar_sarsa --numAgents 2 --numOpponents 3 --numEpisodes 0 --numEpisodesTest 2000 --basePort 7085 \
--weightId conditional_figar_sarsa_lambda_0.5_seed_1_episode_50000 --load --lambda 0.5 > /dev/null

kill -SIGINT $PID
sleep 5
cd ..
