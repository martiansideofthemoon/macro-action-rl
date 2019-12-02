#!/bin/bash

stdbuf -oL ./HFO/bin/HFO --offense-npcs 3 --defense-npcs 1 --defense-agents 2 \
--port 7020 --no-logging --headless --deterministic --trials 2000 --seed 1 > logs/action_space_sarsa.log 2>&1 &

PID=$!
cd action_space_sarsa
sleep 5

./action_space_sarsa --numAgents 2 --numOpponents 3 --numEpisodes 0 --numEpisodesTest 2000 --basePort 7020 \
--weightId action_space_sarsa_lambda_0.95_seed_1_episode_50000 --load --lambda 0.95 > /dev/null

kill -SIGINT $PID
sleep 5
cd ..
