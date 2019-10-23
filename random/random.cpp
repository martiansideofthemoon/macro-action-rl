#include <iostream>
#include <vector>
#include <HFO.hpp>
#include <cstdlib>
#include <thread>
#include "SarsaAgent.h"
#include "CMAC.h"
#include <unistd.h>

// Before running this program, first Start HFO server:
// $./bin/HFO --offense-agents numAgents

void printUsage() {
    std::cout << "Usage:123 ./high_level_sarsa_agent [Options]" << std::endl;
    std::cout << "Options:" << std::endl;
    std::cout << "  --numAgents <int>        Number of SARSA agents" << std::endl;
    std::cout << "                           Default: 0" << std::endl;
    std::cout << "  --numEpisodes <int>      Number of episodes to run" << std::endl;
    std::cout << "                           Default: 10" << std::endl;
    std::cout << "  --numEpisodesTest <int>  Number of episodes to test" << std::endl;
    std::cout << "                           Default: 10" << std::endl;
    std::cout << "  --basePort <int>         SARSA agent base port" << std::endl;
    std::cout << "                           Default: 6001" << std::endl;
    std::cout << "  --numOpponents           Sets the number of opponents" << std::endl;
    std::cout << "  --step                   Sets the persistent step size" << std::endl;
    std::cout << "  --help                   Displays this help and exit" << std::endl;
}

// Convert int to hfo::Action
inline hfo::action_t toAction(int action, const std::vector<float>& state_vec) {
    hfo::action_t a;
    switch (action) {
    case 0:
        a = hfo::MOVE;
        break;
    case 1:
        a = hfo::REDUCE_ANGLE_TO_GOAL;
        break;
    case 2:
        a = hfo::GO_TO_BALL;
        break;
    case 3:
        a = hfo::NOOP;
        break;
    case 4:
        a = hfo::DEFEND_GOAL;
        break;
    default :
        a = hfo::MARK_PLAYER;
        break;
    }
    return a;
}

void offenseAgent(int port, int numOpponents, int numEpi, int numEpiTest, int step) {

    // Number of actions
    int numA = 5 + numOpponents; //DEF_GOAL+MOVE+GTB+NOOP+RATG+MP(unum)

    hfo::HFOEnvironment hfo;
    hfo::status_t status;
    hfo::action_t a;
    int action = -1;
    hfo.connectToServer(hfo::HIGH_LEVEL_FEATURE_SET, "../HFO/bin/teams/base/config/formations-dt", port, "localhost", "base_right", false, "");

    for (int episode = 0; episode < (numEpi + numEpiTest); episode++) {
        status = hfo::IN_GAME;
        action = -1;
        int count_steps = 0;
        double unum = -1;
        while (status == hfo::IN_GAME) {
            const std::vector<float>& state_vec = hfo.getState();
            if (count_steps != step && action >= 0 && (a != hfo :: MARK_PLAYER ||  unum > 0)) {
                count_steps ++;
                if (a == hfo::MARK_PLAYER) {
                    hfo.act(a, unum);
                    //std::cout << "MARKING" << unum <<"\n";
                } else {
                    hfo.act(a);
                }
                status = hfo.step();
                continue;

            } else {
                count_steps = 0;
            }

            // Get raw action
            action = (int)(drand48() * numA) % numA;

            // Get hfo::Action
            a = toAction(action, state_vec);
            if (a == hfo::MARK_PLAYER) {
                unum = state_vec[(state_vec.size() - 1 - (action - 5) * 3)];
                hfo.act(a, unum);
            } else {
                hfo.act(a);
            }
            count_steps++;
            status = hfo.step();
        }
    }
}

int main(int argc, char **argv) {

    int numAgents = 0;
    int numEpisodes = 10;
    int numEpisodesTest = 10;
    int basePort = 6000;
    int numOpponents = 0;
    int step = 10;
    for (int i = 0; i < argc; i++) {
        std::string param = std::string(argv[i]);
        std::cout << param << "\n";
    }
    for(int i = 1; i < argc; i++) {
        std::string param = std::string(argv[i]);
        if(param == "--numAgents") {
            numAgents = atoi(argv[++i]);
        } else if(param == "--numEpisodes") {
            numEpisodes = atoi(argv[++i]);
        } else if(param == "--numEpisodesTest") {
            numEpisodesTest = atoi(argv[++i]);
        } else if(param == "--basePort") {
            basePort = atoi(argv[++i]);
        } else if(param == "--numOpponents") {
            numOpponents = atoi(argv[++i]);
        } else if(param == "--step") {
            step = atoi(argv[++i]);
        } else {
            printUsage();
            return 0;
        }
    }
    std::thread agentThreads[numAgents];
    for (int agent = 0; agent < numAgents; agent++) {
        agentThreads[agent] = std::thread(offenseAgent, basePort, numOpponents, numEpisodes, numEpisodesTest, step);
        sleep(5);
    }
    for (int agent = 0; agent < numAgents; agent++) {
        agentThreads[agent].join();
    }
    return 0;
}

