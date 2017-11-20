#!/bin/bash

./HFO/bin/HFO --port 4000 --offense-npcs 2 --defense-npcs 1 --defense-agents 1 --headless --no-logging&
pid=$!
sleep 5
cd reg_sarsa
./reg_sarsa --numAgents 1 --basePort 4000 --numOpponents 2 --regReward 2 --numEpisodes 100
kill -9 $pid
sleep 5
