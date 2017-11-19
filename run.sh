#!/bin/bash

./HFO/bin/HFO --offense-npcs 2 --defense-npcs 1 --defense-agents 1 --headless&
sleep 5
cd di_sarsa
./di_sarsa --numAgents 1 --numOpponents 2 --step 1 --numEpisodes 100
