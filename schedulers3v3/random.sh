#!/bin/bash

stdbuf -oL ./HFO/bin/HFO --offense-npcs 3 --defense-npcs 1 --defense-agents 2 \
--port 7300 --no-logging --headless --deterministic --trials 2000 --seed 1 > logs/random.log 2>&1 &

PID=$!
cd random
sleep 5

./random --numAgents 2 --numOpponents 3 --numEpisodes 0 --numEpisodesTest 2000 --basePort 7300 --step 32

kill -SIGINT $PID
sleep 5
cd ..
