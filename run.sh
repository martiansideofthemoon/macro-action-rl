#!/bin/bash

./HFO/bin/HFO --offense-npcs 2 --defense-npcs 2 --defense-agents 1 &
sleep 5
cd di_sarsa
./di_sarsa --numAgents 1 --numOpponents 2 --step 10 &
