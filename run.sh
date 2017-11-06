./HFO/bin/HFO --offense-npcs 3 --defense-npcs 1 --defense-agents 2 &
sleep 5
./high_level_sarsa_agent --numAgents 2 --numOpponents 3 &
# sleep 5
# ./high_level_sarsa_agent --numAgents 1 
