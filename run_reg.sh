#!/bin/bash

./HFO/bin/HFO --offense-npcs 2 --defense-npcs 1 --defense-agents 1 &
sleep 5
cd reg_sarsa
./reg_sarsa --numAgents 1 --numOpponents 2 --regReward 0.01
